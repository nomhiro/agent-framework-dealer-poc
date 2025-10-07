from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MCP_ENDPOINT: str = "http://localhost:7071/api/mcp/call"
    MOCK_MCP: bool = True
    OPENAI_API_KEY: str | None = None

    model_config = {"extra": "ignore", "env_file": ".env"}


settings = Settings()
