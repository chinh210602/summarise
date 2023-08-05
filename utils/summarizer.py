from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Summarizer():
    def __init__(self, model_name, device = "cpu"):
        """

        """
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.device = device

    def summarize(self, text, tensors_type, padding):
        """

        """
        tokenized_text = self.tokenizer(text,
                                        return_tensors = tensors_type,
                                        padding = padding).to(self.device)
        
        input_ids = tokenized_text["input_ids"]
        attention_masks = tokenized_text["attention_masks"]

        outputs = self.model.generate(
        input_ids=input_ids, attention_mask=attention_masks,
        max_length=256,
        early_stopping=True,
        num_beams = 20
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens = True, clean_up_tokenization_spaces = True)
