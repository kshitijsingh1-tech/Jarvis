import os
from ai_os.ai_provider import generateCode

# Code Generation Tools for Engineering Students

def write_engineering_code(request: str, target_file: str) -> str:
    """
    JARVIS: Writes code to a file based on an engineering request.
    Specializes in Python, MATLAB, and C++.
    """
    system_prompt = (
        "You are JARVIS, an expert engineering assistant. "
        "Generate production-grade, well-commented code. "
        "Return ONLY the code, no markdown blocks, no explanations. "
        "Focus on numerical accuracy, engineering stability, and performance."
    )

    try:
        # Request code from the Mistral/Code-configured provider
        code = generateCode(request, system_prompt=system_prompt)
        
        # Ensure the target directory exists in our data/ workspace
        # We constrain it to d:/lucky-ai/data/ for safety
        base_dir = "D:/lucky-ai/data/generated_code"
        os.makedirs(base_dir, exist_ok=True)
        
        file_path = os.path.join(base_dir, target_file)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        return f"JARVIS: Engineering code written to {file_path}. Request: '{request}'"
    except Exception as e:
        return f"JARVIS Code Error: {str(e)}"
