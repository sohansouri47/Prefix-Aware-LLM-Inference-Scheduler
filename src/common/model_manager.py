from vllm import LLM, SamplingParams
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModelManager:
    def __init__(self):
        self.llm = None
        self.sampling_params = None

    def init_model(self):
        if self.llm is None:
            logging.info("[ModelManager] Loading model...")
            self.llm = LLM(model="facebook/opt-125m",enable_prefix_caching=True)
            self.sampling_params = SamplingParams(
                temperature=0.8, top_p=0.95,max_tokens=6
            )

    def get(self):
        return self.llm, self.sampling_params


model_manager = ModelManager()
