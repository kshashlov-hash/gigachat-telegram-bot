
def is_palindrome(s):
    cleaned = ""
    for char in s:
      if char.isalnum():
        cleaned = cleaned + char.lower()
    if cleaned[::-1] == cleaned:
        return True
    else:
        return False

print(is_palindrome("A man, a plan, a canal: Panama"))
print(is_palindrome("Hello world"))