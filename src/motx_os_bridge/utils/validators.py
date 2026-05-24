import re


class SecurityValidator:
    DANGEROUS_KEYWORDS = [
        "del /s", "rm -rf", "format", "wipe", "mkfs", "dd if=/dev/zero",
        "system32", "boot", "windows/system", "etc/", "root/", "sudo",
        "chmod 777", "chown root"
    ]

    @staticmethod
    def is_safe(instruction: str) -> bool:
        """Check if instruction is safe to execute"""
        lower_inst = instruction.lower()
        
        for keyword in SecurityValidator.DANGEROUS_KEYWORDS:
            if keyword in lower_inst:
                return False
        
        return True

    @staticmethod
    def validate_path(path: str) -> bool:
        """Check if path is valid and not trying to escape"""
        # Prevent directory traversal
        if ".." in path or "~" in path:
            return False
        
        # Check for suspicious patterns
        if re.search(r'[<>:"|?*]', path):
            return False
        
        return True

    @staticmethod
    def validate_url(url: str) -> bool:
        """Check if URL is valid"""
        pattern = r'^https?://(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?|localhost)'
        return bool(re.match(pattern, url))
