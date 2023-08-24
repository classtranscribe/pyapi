import whisper

class whisper:
  def __init__(self) -> None:
    self.model = whisper.load_model("base")
    
  def transcribe(self, audio):
    result = self.model.transcribe(audio)
    return result
