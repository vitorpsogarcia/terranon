class AssetNotFoundException(Exception):
    """Exception raised when an asset is not found in the AssetManager."""
    def __init__(self, asset_name: str, message: str = "Asset not loaded"):
        self.asset_name = asset_name
        self.message = f"{message}: {asset_name}"
        super().__init__(self.message)
