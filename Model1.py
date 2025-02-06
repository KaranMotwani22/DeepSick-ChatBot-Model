import pandas as pd
import spacy
from typing import List, Dict, Union

class DataFrameQAModel:
    def __init__(self, dataframes: Union[pd.DataFrame, List[pd.DataFrame]], 
                 source_names: List[str] = None):
        """
        Initialize with one or more DataFrames
        :param dataframes: Single DataFrame or list of DataFrames
        :param source_names: Optional names for tracking sources
        """
        self.df = self._combine_dataframes(dataframes, source_names)
        # self.nlp = spacy.load("en_core_web_sm")
        self.nlp = spacy.load("en_core_web_trf") 
        self.column_synonyms = {
            'email': ['email', 'contact', 'mail'],
            'position': ['position', 'role', 'title'],
            'salary': ['salary', 'income', 'pay'],
            'department': ['department', 'team', 'division'],
            # Add more mappings as needed
        } 
        self._expand_synonyms_using_word_embeddings()
        
    def _expand_synonyms_using_word_embeddings(self):
        # Example: Use spaCy's vectors to find similar terms
        for col in self.df.columns:
            if col not in self.column_synonyms:
                self.column_synonyms[col] = []
            # Find similar words (pseudocode)
            similarity_threshold = 0.6
            for word in self.nlp.vocab:
                if word.has_vector and word.is_lower:
                    similarity = self.nlp(col).similarity(word)
                    if similarity > similarity_threshold:
                        self.column_synonyms[col].append(word.text)

    def _combine_dataframes(self, dataframes, source_names) -> pd.DataFrame:
        """Combine multiple DataFrames with source tracking"""
        if not isinstance(dataframes, list):
            dataframes = [dataframes]

        combined = []
        for idx, df in enumerate(dataframes):
            df = df.copy()
            df['source'] = source_names[idx] if source_names else f'dataframe_{idx+1}'
            combined.append(df)

        return pd.concat(combined, ignore_index=True)

    def _extract_entities(self, question: str) -> Dict:
        doc = self.nlp(question)
        entities = {
            "name": None,
            "attribute": None,
            "comparison": None
        }

        # Extract person name (PERSON entity)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["name"] = ent.text

        # Extract attribute and potential comparisons
        for token in doc:
            lower_token = token.text.lower()
            
            # Check attribute synonyms
            for col, synonyms in self.column_synonyms.items():
                if lower_token in synonyms:
                    entities["attribute"] = col
                    break
            
            # Detect comparison operators
            if token.text.lower() in ['above', 'over', 'more than']:
                entities["comparison"] = ('>', self._extract_number(question))
            elif token.text.lower() in ['below', 'under', 'less than']:
                entities["comparison"] = ('<', self._extract_number(question))

        return entities

    def _extract_number(self, text: str) -> float:
        """Extract numeric values from text"""
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'CARDINAL':
                try:
                    return float(ent.text)
                except ValueError:
                    continue
        return None

    def _search_data(self, entities: Dict) -> pd.DataFrame:
        """Search combined DataFrame based on extracted entities"""
        query = []
        
        # Name filter
        if entities["name"]:
            query.append(f'name.str.contains("{entities["name"]}", case=False)')
        
        # Attribute comparison
        if entities["comparison"]:
            op, value = entities["comparison"]
            if value and entities["attribute"]:
                query.append(f'{entities["attribute"]} {op} {value}')
        
        # Build final query
        if query:
            try:
                return self.df.query(' & '.join(query))
            except:
                return pd.DataFrame()
        
        return self.df

    def answer_question(self, question: str) -> str:
        """Process question and return formatted answer"""
        entities = self._extract_entities(question)
        results = self._search_data(entities)
        
        if results.empty:
            return "No matching records found."
        
        # Format response
        response = []
        for _, row in results.iterrows():
            if entities["attribute"]:
                line = (f"{row['name']} ({row['source']}): "
                       f"{entities['attribute']} = {row.get(entities['attribute'], 'N/A')}")
            else:
                line = (f"{row['name']} ({row['source']}): " +
                        ", ".join([f"{k}: {v}" for k, v in row.items() 
                                  if k not in ['name', 'source']]))
            response.append(line)
        
        return "\n".join(response)

# Example Usage
if __name__ == "__main__":
    # Create sample DataFrames
    df1 = pd.DataFrame({
        "name": ["John Doe", "Jane Smith"],
        "email": ["john@company.com", "jane@company.com"],
        "salary": [120000, 150000]
    })
    
    df2 = pd.DataFrame({
        "name": ["Alice Brown", "Bob Johnson"],
        "position": ["Data Scientist", "Marketing Manager"],
        "salary": [90000, 95000]
    })
    
    # Initialize model with DataFrames
    qa_model = DataFrameQAModel(
        dataframes=[df1, df2],
        source_names=["engineering", "marketing"]
    )
    
    questions = [
        "Who earns more than 100000?",
        "What's Jane Smith's email?",
        "Show me people earning under 95000",
        "What position does Alice Brown have?",
        "Tell me about Bob Johnson"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        print(f"A: {qa_model.answer_question(question)}\n")