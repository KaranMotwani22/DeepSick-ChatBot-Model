import json
import spacy
from jsonpath_ng import parse

class JSONQAModel:
    def __init__(self, json_file_path):
        self.json_data = self._load_json(json_file_path)
        self.nlp = spacy.load("en_core_web_sm")
        self.attribute_synonyms = {
            "email": ["email", "contact", "mail"],
            "position": ["position", "role", "title", "job"],
            "age": ["age", "years old"],
            # Add more mappings as needed
        }

    def _load_json(self, file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    def _extract_entities(self, question):
        doc = self.nlp(question)
        entities = {
            "name": None,
            "attribute": None
        }
        
        # Extract name (PERSON entity)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["name"] = ent.text
        
        # Extract attribute using token analysis and synonyms
        for token in doc:
            if token.pos_ == "NOUN" or token.pos_ == "PROPN":
                for key, synonyms in self.attribute_synonyms.items():
                    if token.text.lower() in synonyms:
                        entities["attribute"] = key
                        break
        
        return entities

    def _search_json(self, name, attribute):
        try:
            # Proper JSONPath syntax for jsonpath-ng
            if attribute:
                # For specific attribute search
                print(f"Debug: JSONPath Query = $..[?(@.name == \"{name}\")].{attribute}")
                # jsonpath_expr = parse(f"$..[?name == '{name}'].{attribute}")
                jsonpath_expr = parse(f"$..[?(@.name == \"{name}\")].{attribute}")


            else:
                # For general entity search
                jsonpath_expr = parse(f"$..[?name == '{name}']")
            
            matches = [match.value for match in jsonpath_expr.find(self.json_data)]
            return matches
        except Exception as e:
            print(f"Search Error: {str(e)}")
            return []

    def answer_question(self, question):
        entities = self._extract_entities(question)
        if not entities["name"]:
            return "Could not identify a person in your question."
        
        results = self._search_json(entities["name"], entities["attribute"])
        
        if not results:
            if entities["attribute"]:
                return f"No {entities['attribute']} found for {entities['name']}."
            return f"No information found about {entities['name']}."

        
        if entities["attribute"]:
            return f"{entities['name']}'s {entities['attribute']} is {results[0]}."
        else:
            return f"Here's what I found about {entities['name']}: {results[0]}."

# Example Usage
if __name__ == "__main__":
    # Sample JSON file (employees.json)
    sample_json = [
        {
            "name": "John Doe",
            "email": "john@company.com",
            "position": "Software Engineer",
            "age": 30
        },
        {
            "name": "Jane Smith",
            "email": "jane@company.com",
            "position": "Product Manager",
            "age": 35
        }
    ]
    
    # Save sample JSON to file
    with open("employees.json", "w") as f:
        json.dump(sample_json, f)
    
    # Initialize and test the model
    qa_model = JSONQAModel("employees.json")
    
    questions = [
        "What is John Doe's email?",
        "What role does Jane Smith have?",
        "How old is John Doe?",
        "Tell me about Jane Smith."
    ]
    
    for question in questions:
        print(f"Q: {question}")
        print(f"A: {qa_model.answer_question(question)}\n")