"""
SNIP Token Configuration Registry
Contains contract addresses and metadata for major SNIP tokens
"""
import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SNIPTokenConfig:
    """Configuration for a SNIP token"""
    symbol: str
    name: str
    contract_address: str
    decimals: int
    code_hash: Optional[str] = None
    token_type: str = "snip20"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.contract_address.startswith('secret1'):
            raise ValueError(f"Invalid contract address for {self.symbol}: {self.contract_address}")
        if self.decimals < 0:
            raise ValueError(f"Invalid decimals for {self.symbol}: {self.decimals}")


# Official Secret Network SNIP Token Registry (Mainnet)
SNIP_TOKEN_CONTRACTS: Dict[str, SNIPTokenConfig] = {
    # === NATIVE TOKENS ===
    "sscrt": SNIPTokenConfig(
        symbol="sscrt",
        name="Secret SCRT",
        contract_address="secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek",
        decimals=6,
        code_hash="af74387e276be8874f07bec3a87023ee49b0e7ebe08178c49d0a49c3c98ed60e",
        token_type="snip20"
    ),
    "silk": SNIPTokenConfig(
        symbol="silk",
        name="Silk Stablecoin",
        contract_address="secret1fl449muk5yq8dlad7a22nje4p5d2pnsgymhjfd",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "shd": SNIPTokenConfig(
        symbol="shd",
        name="Shade",
        contract_address="secret153wu605vvp934xhd4k9dtd640zsep5jkesstdm",
        decimals=8,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),

    # === STAKING DERIVATIVES ===
    "stkd-scrt": SNIPTokenConfig(
        symbol="stkd-scrt",
        name="Shade SCRT staking derivative",
        contract_address="secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4",
        decimals=6,
        code_hash="f6be719b3c6feb498d3554ca0398eb6b7e7db262acb33f84a8f12106da6bbb09",
        token_type="snip20"
    ),
    "sstjuno": SNIPTokenConfig(
        symbol="sstjuno",
        name="Secret stJUNO",
        contract_address="secret1097nagcaavlkchl87xkqptww2qkwuvhdnsqs2v",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "sstatom": SNIPTokenConfig(
        symbol="sstatom",
        name="Secret stATOM",
        contract_address="secret155w9uxruypsltvqfygh5urghd5v0zc6f9g69sq",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "sstluna": SNIPTokenConfig(
        symbol="sstluna",
        name="Secret stLUNA",
        contract_address="secret1rkgvpck36v2splc203sswdr0fxhyjcng7099a9",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "sstosmo": SNIPTokenConfig(
        symbol="sstosmo",
        name="Secret stOSMO",
        contract_address="secret1jrp6z8v679yaq65rndsr970mhaxzgfkymvc58g",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),

    # === MAJOR CROSS-CHAIN TOKENS ===
    "sinj": SNIPTokenConfig(
        symbol="sinj",
        name="Secret INJ",
        contract_address="secret14706vxakdzkz9a36872cs62vpl5qd84kpwvpew",
        decimals=18,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "swbtc": SNIPTokenConfig(
        symbol="swbtc",
        name="Secret WBTC",
        contract_address="secret1v2kgmfwgd2an0l5ddralajg5wfdkemxl2vg4jp",
        decimals=8,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "susdt": SNIPTokenConfig(
        symbol="susdt",
        name="Secret USDT",
        contract_address="secret1htd6s29m2j9h45knwkyucz98m306n32hx8dww3",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "snobleusdc": SNIPTokenConfig(
        symbol="snobleusdc",
        name="Secret Noble USDC",
        contract_address="secret1chsejpk9kfj4vt9ec6xvyguw539gsdtr775us2",
        decimals=6,
        code_hash="5a085bd8ed89de92b35134ddd12505a602c7759ea25fb5c089ba03c8535b3042",
        token_type="snip20"
    ),
    "sdydx": SNIPTokenConfig(
        symbol="sdydx",
        name="Secret dYdX",
        contract_address="secret13lndcagy53wfzh69rtv0dex3a7cks0dv5emwke",
        decimals=18,
        code_hash="5a085bd8ed89de92b35134ddd12505a602c7759ea25fb5c089ba03c8535b3042",
        token_type="snip20"
    ),
    "sarch": SNIPTokenConfig(
        symbol="sarch",
        name="Secret ARCH",
        contract_address="secret188z7hncvphw4us4h6uy6vlq4qf20jd2vm2vu8c",
        decimals=18,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),
    "sakt": SNIPTokenConfig(
        symbol="sakt",
        name="Secret AKT",
        contract_address="secret168j5f78magfce5r2j4etaytyuy7ftjkh4cndqw",
        decimals=6,
        code_hash="5a085bd8ed89de92b35134ddd12505a602c7759ea25fb5c089ba03c8535b3042",
        token_type="snip20"
    ),
    "stia": SNIPTokenConfig(
        symbol="stia",
        name="Secret Celestia",
        contract_address="secret1s9h6mrp4k9gll4zfv5h78ll68hdq8ml7jrnn20",
        decimals=6,
        code_hash="638a3e1d50175fbcb8373cf801565283e3eb23d88a9b7b7f99fcc5eb1e6b561e",
        token_type="snip20"
    ),

    # === ECOSYSTEM TOKENS ===
    "butt": SNIPTokenConfig(
        symbol="butt",
        name="BTN.group coin",
        contract_address="secret1yxcexylwyxlq58umhgsjgstgcg2a0ytfy4d9lt",
        decimals=6,
        code_hash="f8b27343ff08290827560a1ba358eece600c9ea7f403b02684ad87ae7af0f288",
        token_type="snip20"
    ),
    "alter": SNIPTokenConfig(
        symbol="alter",
        name="Alter",
        contract_address="secret12rcvz0umvk875kd6a803txhtlu7y0pnd73kcej",
        decimals=6,
        code_hash="d4f32c1bca133f15f69d557bd0722da10f45e31e5475a12900ca1e62e63e8f76",
        token_type="snip20"
    ),
    "amber": SNIPTokenConfig(
        symbol="amber",
        name="Amber",
        contract_address="secret1s09x2xvfd2lp2skgzm29w2xtena7s8fq98v852",
        decimals=6,
        code_hash="9a00ca4ad505e9be7e6e6dddf8d939b7ec7e9ac8e109d2c9a8fb6bb7b8c0a820",
        token_type="snip20"
    )
}

# Configuration settings
SECRET_LCD_ENDPOINT = os.getenv("SECRET_LCD_ENDPOINT", "https://lcd.secret.adrius.starshell.net/")
SNIP_TOKEN_CACHE_TTL = int(os.getenv("SNIP_TOKEN_CACHE_TTL", "300"))
VIEWING_KEY_STORAGE_BACKEND = os.getenv("VIEWING_KEY_STORAGE_BACKEND", "memory")
SNIP_TOKEN_SERVICE_ENABLED = os.getenv("SNIP_TOKEN_SERVICE_ENABLED", "true").lower() == "true"

# Batch Query Contract for SNIP-20 tokens (from dash.scrt.network)
BATCH_QUERY_CONTRACT_ADDRESS = "secret17gnlxnwux0szd7qhl90ym8lw22qvedjz4v09dm"
BATCH_QUERY_CONTRACT_CODE_HASH = "72a09535b77b76862f7b568baf1ddbe158a2e4bbd0f0879c69ada9b398e31c1f"

# Query timeouts
HTTP_TIMEOUT = int(os.getenv("SNIP_HTTP_TIMEOUT", "30"))
QUERY_RETRY_COUNT = int(os.getenv("SNIP_QUERY_RETRY_COUNT", "3"))


def get_token_config(symbol: str) -> Optional[SNIPTokenConfig]:
    """Get token configuration by symbol"""
    return SNIP_TOKEN_CONTRACTS.get(symbol.lower())


def is_supported_token(symbol: str) -> bool:
    """Check if a token symbol is supported"""
    return symbol.lower() in SNIP_TOKEN_CONTRACTS


def get_supported_tokens() -> Dict[str, SNIPTokenConfig]:
    """Get all supported token configurations"""
    return SNIP_TOKEN_CONTRACTS.copy()