import re

def needs_artifact(message: str) -> bool:
    """
    Determines if the user request should generate an artifact (HTML/Markdown/Code/UI).
    Uses keyword heuristics for fast execution.
    """
    message_lower = message.lower()
    
    # Heuristics based on artifact keywords
    artifact_keywords = [
        "html", "css", "landing page", "dashboard", "report", "resume", 
        "documentation", "markdown", "ui component", "react component",
        "mockup", "prototype", "website", "web page"
    ]
    
    if any(kw in message_lower for kw in artifact_keywords):
        return True
        
    # Explicit command check
    if re.search(r'\b(create|generate|build|write|code).*(app|page|html|css|dashboard|component|markdown)\b', message_lower):
        return True
        
    return False
