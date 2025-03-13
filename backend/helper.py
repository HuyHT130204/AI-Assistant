import re


def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None


def remove_words(input_string, words_to_remove): 
    # Loại bỏ từng từ một để tránh loại bỏ phần của tên
    result = input_string
    for word in words_to_remove:
        # Chỉ loại bỏ từ nếu nó là một từ hoàn chỉnh (có khoảng trắng trước và sau)
        pattern = r'\b' + re.escape(word) + r'\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Loại bỏ khoảng trắng thừa
    result = re.sub(r'\s+', ' ', result).strip()
    return result


def extract_fb_term(command, action_type):
    """
    Extract name from Facebook-related commands
    
    Args:
        command (str): The command string to parse
        action_type (str): Either "find" or "message" to determine pattern
    
    Returns:
        str or None: The extracted name or None if no match
    """
    if action_type == "find":
        # Pattern for finding someone on Facebook
        pattern = r'find\s+(.*?)\s+on\s+facebook'
    elif action_type == "message":
        # Pattern for messaging someone on Facebook
        pattern = r'send\s+message\s+to\s+(.*?)\s+on\s+facebook'
    else:
        return None
        
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None