# This file is part of fungiarticlesearch.
#
# fungiarticlesearch is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# fungiarticlesearch is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with fungiarticlesearch.
# If not, see <https://www.gnu.org/licenses/>.

import base64
from typing import  Optional
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ApiKeyManager:
    """
    Class for storing an api key.
    """

    _API_KEY_FILE = Path('./.fasdata/secret')
    _ENCODING = 'utf-8'
    _STATIC_SALT = b' \xdf\xee\xaa*\x88\xb7D\xc1\xf9m\x8f\xe8\xffFT'  # is randomly generated

    @staticmethod
    def _generate_key_from_password(password: str) -> Fernet:
        """
        Generates encryption key from the password and passes it
        to Fernet class, which will be retured.
        Uses PBKDF2 method.

        :param password: a password used for encryption
        :return: Fernet class object with the generated key.
        """

        password_bytes = bytes(password, encoding='utf8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=ApiKeyManager._STATIC_SALT,
            iterations=390000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        return Fernet(key)

    def save_key(self, key: str, password: str) -> None:
        """
        Encrypts and saves API key to the file API_KEY_FILE.

        :param key: key to save.
        :param password: password used to encode the key.
        """

        fernet = self._generate_key_from_password(password)
        encrypted_key = fernet.encrypt(bytes(key, encoding=self._ENCODING))

        self._API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with self._API_KEY_FILE.open(mode='wb') as f:
            f.write(encrypted_key)

    def is_key_saved(self) -> bool:
        return self._API_KEY_FILE.exists()

    def read_key(self, password: str) -> Optional[str]:
        """
        Reads and decrypts API key to the file API_KEY_FILE.
        If key is not saved, None is returned.

        :param password: password used to encode the key.
        :raise ValueError: if password is incorrect
        :return: the API key.
        """

        if not self.is_key_saved():
            return None

        fernet = self._generate_key_from_password(password)

        with self._API_KEY_FILE.open(mode='rb') as f:
            key_raw = f.read()

        try:
            return fernet.decrypt(key_raw).decode(self._ENCODING)
        except InvalidToken:
            raise ValueError('Given encoded API key or password is incorrect.')


