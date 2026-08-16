
class InvalidURLException(Exception):
    pass

class InvalidVideoIDException(Exception):
    pass

class VideoUnavailableException(Exception):
    pass

class TranscriptDisabledException(Exception):
    pass

class QdrantCollectionNotFoundException(Exception):
    pass

class NoChunksFoundException(Exception):
    pass

class VideoNotProcessedException(Exception):
    pass