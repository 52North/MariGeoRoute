class DownloaderBase:
    """Downloader base class"""
    def __init__(self, downloader_type, **kwargs):
        self.downloader_type = downloader_type
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)

    def download(self, **kwargs):
        raise NotImplementedError(".download() must be overridden.")
