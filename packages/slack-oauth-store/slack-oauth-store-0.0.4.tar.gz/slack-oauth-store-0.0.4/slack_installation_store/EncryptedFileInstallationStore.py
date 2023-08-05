import logging
import json
from logging import Logger
from pathlib import Path
from typing import Optional
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation

import pyAesCrypt
import io

class EncryptedFileInstallationStore(FileInstallationStore):
    
    def __init__(self,
                *,
                encryption_key: str,
                base_dir: str = str(Path.home()) + "/.bolt-app-installation",
                historical_data_enabled: bool = True,
                client_id: Optional[str] = None,
                logger: Logger = logging.getLogger(__name__)) -> None:
        self.encryption_key = encryption_key
        super().__init__(base_dir=base_dir, 
                        historical_data_enabled=historical_data_enabled, 
                        client_id=client_id, 
                        logger=logger)

    def encrypt(self, raw_data):
        if not self.encryption_key:
            raise ValueError("Encryption key can not be empty.")
        buffer_size = 64 * 1024
        # plaintext binary stream
        raw_stream = io.BytesIO(raw_data)
        # initialize ciphertext binary stream
        cipher_stream = io.BytesIO()
        # encrypt stream
        pyAesCrypt.encryptStream(raw_stream, cipher_stream, self.encryption_key, buffer_size)
        encrypted_data = cipher_stream.getvalue()
        return encrypted_data

    def decrypt(self, encrypted_data):
        if not self.encryption_key:
            raise ValueError("Encryption key can not be empty.")
        buffer_size = 64 * 1024
        # ciphertext binary stream
        cipher_stream = io.BytesIO(encrypted_data)
        # get ciphertext length
        cipher_len = len(cipher_stream.getvalue())
        # initialize decrypted binary stream
        decrypt_stream = io.BytesIO()
        # decrypt stream
        pyAesCrypt.decryptStream(cipher_stream, decrypt_stream, self.encryption_key, buffer_size, cipher_len)
        return decrypt_stream.getvalue()

    def save_to_file(self, file_path, data):
        enc_data = self.encrypt(data.encode('utf-8'))
        with open(file_path, "wb") as f:
            f.write(enc_data)

    def read_from_file(self, file_path):
        with open(file_path, "rb") as f:
            enc_data = f.read()
        data = self.decrypt(enc_data)
        return json.loads(data)

    def save(self, installation: Installation):
        none = "none"
        e_id = installation.enterprise_id or none
        t_id = installation.team_id or none
        team_installation_dir = f"{self.base_dir}/{e_id}-{t_id}"
        self._mkdir(team_installation_dir)

        self.save_bot(installation.to_bot())

        if self.historical_data_enabled:
            history_version: str = str(installation.installed_at)

            # per workspace
            entity: str = json.dumps(installation.__dict__)
            self.save_to_file(f"{team_installation_dir}/installer-latest", entity)
            self.save_to_file(f"{team_installation_dir}/installer-{history_version}", entity)

            # per workspace per user
            u_id = installation.user_id or none
            entity: str = json.dumps(installation.__dict__)
            self.save_to_file(f"{team_installation_dir}/installer-{u_id}-latest", entity)
            self.save_to_file(f"{team_installation_dir}/installer-{u_id}-{history_version}",entity)

        else:
            u_id = installation.user_id or none
            installer_filepath = f"{team_installation_dir}/installer-{u_id}-latest"
            self.save_to_file(installer_filepath, json.dumps(installation.__dict__))

    def save_bot(self, bot: Bot):
        none = "none"
        e_id = bot.enterprise_id or none
        t_id = bot.team_id or none
        team_installation_dir = f"{self.base_dir}/{e_id}-{t_id}"
        self._mkdir(team_installation_dir)

        if self.historical_data_enabled:
            history_version: str = str(bot.installed_at)

            entity: str = json.dumps(bot.__dict__)
            self.save_to_file(f"{team_installation_dir}/bot-latest", entity)
            self.save_to_file(f"{team_installation_dir}/bot-{history_version}", entity)
        else:
            self.save_to_file(f"{team_installation_dir}/bot-latest", json.dumps(bot.__dict__))

    async def async_find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        return self.find_bot(
            enterprise_id=enterprise_id,
            team_id=team_id,
            is_enterprise_install=is_enterprise_install,
        )

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        none = "none"
        e_id = enterprise_id or none
        t_id = team_id or none
        if is_enterprise_install:
            t_id = none
        bot_filepath = f"{self.base_dir}/{e_id}-{t_id}/bot-latest"
        try:
            data = self.read_from_file(bot_filepath)
            return Bot(**data)
        except FileNotFoundError as e:
            message = f"Installation data missing for enterprise: {e_id}, team: {t_id}: {e}"
            self.logger.debug(message)
            return None    

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        none = "none"
        e_id = enterprise_id or none
        t_id = team_id or none
        if is_enterprise_install:
            t_id = none
        installation_filepath = f"{self.base_dir}/{e_id}-{t_id}/installer-latest"
        if user_id is not None:
            installation_filepath = f"{self.base_dir}/{e_id}-{t_id}/installer-{user_id}-latest"

        try:
            installation: Optional[Installation] = None
            data = self.read_from_file(installation_filepath) 
            installation = Installation(**data)
            # Sync with PR https://github.com/slackapi/python-slack-sdk/pull/1223
            if installation is not None and user_id is not None:
                # Retrieve the latest bot token, just in case
                # See also: https://github.com/slackapi/bolt-python/issues/664
                latest_bot_installation = self.find_installation(
                    enterprise_id=enterprise_id,
                    team_id=team_id,
                    is_enterprise_install=is_enterprise_install,
                )
                if latest_bot_installation is not None and installation.bot_token != latest_bot_installation.bot_token:
                    # NOTE: this logic is based on the assumption that every single installation has bot scopes
                    # If you need to installation patterns without bot scopes in the same S3 bucket,
                    # please fork this code and implement your own logic.
                    installation.bot_id = latest_bot_installation.bot_id
                    installation.bot_user_id = latest_bot_installation.bot_user_id
                    installation.bot_token = latest_bot_installation.bot_token
                    installation.bot_scopes = latest_bot_installation.bot_scopes
                    installation.bot_refresh_token = latest_bot_installation.bot_refresh_token
                    installation.bot_token_expires_at = latest_bot_installation.bot_token_expires_at

            return installation
        except FileNotFoundError as e:
            message = f"Installation data missing for enterprise: {e_id}, team: {t_id}: {e}"
            self.logger.debug(message)
            return None

if __name__ == "main":
    enc = EncryptedFileInstallationStore(encryption_key=None)