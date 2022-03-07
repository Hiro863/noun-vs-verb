import traceback


class SubjectNotProcessedError(Exception):
    def __init__(self, error, message=""):
        self.error = error
        super().__init__(f"Preprocess failed due to {type(self.error).__name__}. \n {traceback.format_exc()} ")
