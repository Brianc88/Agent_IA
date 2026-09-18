"""
Configuración centralizada, leída una sola vez desde variables de entorno.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    server: str
    name: str
    user: str
    password: str
    driver: str

    def connection_string(self) -> str:
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.name};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    agent_db_server: str
    agent_db_name: str
    agent_db_user: str
    agent_db_password: str
    agent_db_driver: str

    his_db_server: str
    his_db_name: str
    his_db_user: str
    his_db_password: str
    his_db_driver: str

    @property
    def agent_db(self) -> DatabaseSettings:
        return DatabaseSettings(
            server=self.agent_db_server,
            name=self.agent_db_name,
            user=self.agent_db_user,
            password=self.agent_db_password,
            driver=self.agent_db_driver,
        )

    @property
    def his_db(self) -> DatabaseSettings:
        return DatabaseSettings(
            server=self.his_db_server,
            name=self.his_db_name,
            user=self.his_db_user,
            password=self.his_db_password,
            driver=self.his_db_driver,
        )


settings = Settings()