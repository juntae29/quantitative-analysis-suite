class KwicEngine:
    @staticmethod
    def get_context(text, keyword, window=10):
        if not text or not keyword:
            return []
        
        words = text.split()
        results = []
        keyword_lower = keyword.lower()
        
        for i, word in enumerate(words):
            if keyword_lower in word.lower():
                start = max(0, i - window)
                left = " ".join(words[start:i])
                end = min(len(words), i + window + 1)
                right = " ".join(words[i+1:end])
                # 표 출력을 위해 구조화된 데이터 반환
                results.append({"Left Context": left, "Keyword": word.upper(), "Right Context": right})
        
        return results