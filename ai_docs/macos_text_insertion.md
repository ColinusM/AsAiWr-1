# macOS Text Insertion Implementation Guide

## Cross-Application Text Insertion Methods

### Method 1: Clipboard-Based Insertion (Most Reliable)

```python
import pyautogui
import pyperclip
import time
from typing import Optional

class ClipboardTextInserter:
    """Reliable text insertion using clipboard method"""
    
    def __init__(self):
        # Configure pyautogui for macOS
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  # Small pause between commands
        
    def insert_text(self, text: str, replace_selection: bool = False) -> bool:
        """
        Insert text using clipboard method
        
        Args:
            text: Text to insert
            replace_selection: If True, replace selected text; if False, append
            
        Returns:
            bool: Success status
        """
        if not text.strip():
            return False
            
        # Save current clipboard content
        original_clipboard = self._get_clipboard_safely()
        
        try:
            # Set new text to clipboard
            pyperclip.copy(text)
            
            # Replace selected text if requested
            if replace_selection:
                pyautogui.hotkey('cmd', 'a')  # Select all
                time.sleep(0.05)  # Brief pause
                
            # Paste the text
            pyautogui.hotkey('cmd', 'v')
            
            # Wait for paste to complete
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            print(f"Text insertion failed: {e}")
            return False
            
        finally:
            # Restore original clipboard after delay
            if original_clipboard is not None:
                time.sleep(0.5)  # Wait for app to process paste
                pyperclip.copy(original_clipboard)
                
    def _get_clipboard_safely(self) -> Optional[str]:
        """Safely get clipboard content"""
        try:
            return pyperclip.paste()
        except Exception:
            return None
            
    def append_text(self, text: str) -> bool:
        """Append text at current cursor position"""
        return self.insert_text(text, replace_selection=False)
        
    def replace_text(self, text: str) -> bool:
        """Replace all text in current field"""
        return self.insert_text(text, replace_selection=True)
```

### Method 2: Direct Keyboard Simulation

```python
import pyautogui
import time
import re

class KeyboardTextInserter:
    """Direct keyboard simulation for text insertion"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # Faster for typing
        
    def type_text_directly(self, text: str, typing_speed: float = 0.01) -> bool:
        """
        Type text directly using keyboard simulation
        
        Args:
            text: Text to type
            typing_speed: Delay between keystrokes
            
        Returns:
            bool: Success status
        """
        try:
            # Handle special characters that need escaping
            cleaned_text = self._clean_text_for_typing(text)
            
            # Type the text with specified speed
            pyautogui.write(cleaned_text, interval=typing_speed)
            
            return True
            
        except Exception as e:
            print(f"Direct typing failed: {e}")
            return False
            
    def _clean_text_for_typing(self, text: str) -> str:
        """Clean text for direct typing"""
        # Remove or escape problematic characters
        # PyAutoGUI has issues with some special characters
        
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Handle other special characters as needed
        return text
        
    def type_with_autocorrect_handling(self, text: str) -> bool:
        """Type text with handling for macOS autocorrect"""
        try:
            # Type text
            self.type_text_directly(text)
            
            # Brief pause to let autocorrect activate
            time.sleep(0.2)
            
            # Press Escape to dismiss any autocorrect popups
            pyautogui.press('escape')
            
            return True
            
        except Exception as e:
            print(f"Typing with autocorrect handling failed: {e}")
            return False
```

### Method 3: macOS Accessibility API (Advanced)

```python
from Cocoa import NSPasteboard, NSStringPboardType, NSWorkspace
import Cocoa
import objc
from PyObjCTools import AppHelper

class AccessibilityTextInserter:
    """Advanced text insertion using macOS Accessibility APIs"""
    
    def __init__(self):
        self.pasteboard = NSPasteboard.generalPasteboard()
        self.workspace = NSWorkspace.sharedWorkspace()
        
    def get_active_application_info(self) -> dict:
        """Get information about the currently active application"""
        try:
            active_app = self.workspace.activeApplication()
            return {
                'name': active_app.get('NSApplicationName', 'Unknown'),
                'bundle_id': active_app.get('NSApplicationBundleIdentifier', ''),
                'pid': active_app.get('NSApplicationProcessIdentifier', 0)
            }
        except Exception as e:
            print(f"Could not get active app info: {e}")
            return {}
            
    def insert_text_via_pasteboard(self, text: str) -> bool:
        """Insert text using NSPasteboard"""
        try:
            # Save current pasteboard content
            current_content = self.pasteboard.stringForType_(NSStringPboardType)
            
            # Set new text
            self.pasteboard.clearContents()
            self.pasteboard.setString_forType_(text, NSStringPboardType)
            
            # Simulate paste command
            pyautogui.hotkey('cmd', 'v')
            
            # Restore pasteboard after delay
            time.sleep(0.5)
            if current_content:
                self.pasteboard.clearContents()
                self.pasteboard.setString_forType_(current_content, NSStringPboardType)
                
            return True
            
        except Exception as e:
            print(f"Pasteboard insertion failed: {e}")
            return False
            
    def check_accessibility_permissions(self) -> bool:
        """Check if app has accessibility permissions"""
        try:
            # Try to get active application - requires accessibility permission
            active_app = self.workspace.activeApplication()
            return active_app is not None
        except Exception:
            return False
            
    def request_accessibility_permissions(self):
        """Guide user to enable accessibility permissions"""
        print("Accessibility permissions required!")
        print("Please enable accessibility access:")
        print("1. System Preferences → Security & Privacy → Privacy")
        print("2. Select 'Accessibility' from sidebar")  
        print("3. Add your Python interpreter or Terminal")
        
        # Open accessibility preferences
        import subprocess
        try:
            subprocess.run([
                "open",
                "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
            ])
        except:
            subprocess.run(["open", "/System/Library/PreferencePanes/Security.prefPane"])
```

### Smart Text Insertion with App-Specific Behavior

```python
class SmartTextInserter:
    """Intelligent text insertion with app-specific optimizations"""
    
    def __init__(self):
        self.clipboard_inserter = ClipboardTextInserter()
        self.keyboard_inserter = KeyboardTextInserter()
        self.accessibility_inserter = AccessibilityTextInserter()
        
        # App-specific behaviors
        self.app_behaviors = {
            'com.apple.dt.Xcode': self._handle_xcode,
            'com.microsoft.VSCode': self._handle_vscode,
            'com.apple.mail': self._handle_mail,
            'com.apple.TextEdit': self._handle_textedit,
            'com.slack.Slack': self._handle_slack,
            'com.tinyspeck.slackmacgap': self._handle_slack,
            'com.discord.Discord': self._handle_discord,
            'org.mozilla.firefox': self._handle_browser,
            'com.google.Chrome': self._handle_browser,
        }
        
    def insert_text_smart(self, text: str, context: dict = None) -> bool:
        """
        Smart text insertion with app-specific handling
        
        Args:
            text: Text to insert
            context: Additional context about the insertion
            
        Returns:
            bool: Success status
        """
        # Get active application info
        app_info = self.accessibility_inserter.get_active_application_info()
        bundle_id = app_info.get('bundle_id', '')
        app_name = app_info.get('name', '')
        
        print(f"Inserting text into: {app_name} ({bundle_id})")
        
        # Try app-specific handler first
        if bundle_id in self.app_behaviors:
            try:
                return self.app_behaviors[bundle_id](text, app_info, context)
            except Exception as e:
                print(f"App-specific handler failed: {e}")
                # Fall back to default method
                
        # Default insertion method
        return self._default_insertion(text, app_info)
        
    def _default_insertion(self, text: str, app_info: dict) -> bool:
        """Default text insertion method"""
        # Try clipboard method first (most reliable)
        if self.clipboard_inserter.insert_text(text):
            return True
            
        # Fall back to direct typing
        return self.keyboard_inserter.type_text_directly(text)
        
    def _handle_xcode(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in Xcode"""
        # In Xcode, often want to add as comments for voice notes
        if not text.strip().startswith('//'):
            text = f"// {text.strip()}"
            
        return self.clipboard_inserter.insert_text(text)
        
    def _handle_vscode(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in VS Code"""
        # VS Code handles clipboard well
        return self.clipboard_inserter.insert_text(text)
        
    def _handle_mail(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in Mail app"""
        # Capitalize first letter for email
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        return self.clipboard_inserter.insert_text(text)
        
    def _handle_textedit(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in TextEdit"""
        return self.clipboard_inserter.insert_text(text)
        
    def _handle_slack(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in Slack"""
        # Slack sometimes has issues with paste, try typing first
        if self.keyboard_inserter.type_text_directly(text, typing_speed=0.005):
            return True
        return self.clipboard_inserter.insert_text(text)
        
    def _handle_discord(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in Discord"""
        # Similar to Slack
        return self._handle_slack(text, app_info, context)
        
    def _handle_browser(self, text: str, app_info: dict, context: dict) -> bool:
        """Handle text insertion in web browsers"""
        # Browsers usually handle clipboard well
        return self.clipboard_inserter.insert_text(text)
```

### Text Formatting and Processing

```python
class TextProcessor:
    """Process and format text before insertion"""
    
    def __init__(self):
        self.formatting_rules = {
            'capitalize_sentences': True,
            'add_punctuation': True,
            'fix_spacing': True,
            'handle_contractions': True
        }
        
    def process_transcribed_text(self, raw_text: str) -> str:
        """Process raw transcribed text for insertion"""
        text = raw_text.strip()
        
        if not text:
            return text
            
        # Apply formatting rules
        if self.formatting_rules['fix_spacing']:
            text = self._fix_spacing(text)
            
        if self.formatting_rules['handle_contractions']:
            text = self._fix_contractions(text)
            
        if self.formatting_rules['add_punctuation']:
            text = self._ensure_punctuation(text)
            
        if self.formatting_rules['capitalize_sentences']:
            text = self._capitalize_sentences(text)
            
        return text
        
    def _fix_spacing(self, text: str) -> str:
        """Fix common spacing issues"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
        
    def _fix_contractions(self, text: str) -> str:
        """Fix common contraction issues"""
        contractions = {
            "can not": "cannot",
            "will not": "won't", 
            "shall not": "shan't",
            "I am": "I'm",
            "you are": "you're",
            "he is": "he's",
            "she is": "she's",
            "it is": "it's",
            "we are": "we're",
            "they are": "they're"
        }
        
        for full, contracted in contractions.items():
            text = re.sub(r'\b' + full + r'\b', contracted, text, flags=re.IGNORECASE)
            
        return text
        
    def _ensure_punctuation(self, text: str) -> str:
        """Ensure text ends with appropriate punctuation"""
        if not text:
            return text
            
        # If doesn't end with punctuation, add period
        if not re.search(r'[.!?]$', text.strip()):
            text = text.strip() + '.'
            
        return text
        
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize first letter of sentences"""
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
            
        # Capitalize after sentence endings
        text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        return text
```

### Error Handling and Fallback Strategies

```python
class RobustTextInserter:
    """Text inserter with comprehensive error handling"""
    
    def __init__(self):
        self.smart_inserter = SmartTextInserter()
        self.text_processor = TextProcessor()
        self.insertion_methods = [
            ('clipboard', self._try_clipboard_insertion),
            ('keyboard', self._try_keyboard_insertion),
            ('accessibility', self._try_accessibility_insertion)
        ]
        
    def insert_with_fallback(self, raw_text: str) -> tuple[bool, str]:
        """
        Insert text with multiple fallback methods
        
        Returns:
            tuple: (success, error_message)
        """
        if not raw_text.strip():
            return False, "Empty text"
            
        # Process the text
        processed_text = self.text_processor.process_transcribed_text(raw_text)
        
        # Try each insertion method
        for method_name, method_func in self.insertion_methods:
            try:
                if method_func(processed_text):
                    print(f"Text inserted successfully using {method_name} method")
                    return True, ""
                    
            except Exception as e:
                print(f"{method_name} method failed: {e}")
                continue
                
        return False, "All insertion methods failed"
        
    def _try_clipboard_insertion(self, text: str) -> bool:
        """Try clipboard-based insertion"""
        return self.smart_inserter.clipboard_inserter.insert_text(text)
        
    def _try_keyboard_insertion(self, text: str) -> bool:
        """Try keyboard simulation insertion"""
        return self.smart_inserter.keyboard_inserter.type_text_directly(text)
        
    def _try_accessibility_insertion(self, text: str) -> bool:
        """Try accessibility API insertion"""
        return self.smart_inserter.accessibility_inserter.insert_text_via_pasteboard(text)
        
    def validate_insertion_environment(self) -> dict:
        """Validate that text insertion will work"""
        results = {
            'clipboard_available': False,
            'accessibility_enabled': False,
            'keyboard_simulation': False,
            'active_app_detected': False
        }
        
        # Test clipboard access
        try:
            original = pyperclip.paste()
            pyperclip.copy("test")
            test_result = pyperclip.paste()
            pyperclip.copy(original or "")
            results['clipboard_available'] = (test_result == "test")
        except:
            pass
            
        # Test accessibility
        try:
            results['accessibility_enabled'] = self.smart_inserter.accessibility_inserter.check_accessibility_permissions()
        except:
            pass
            
        # Test keyboard simulation
        try:
            # This is hard to test without actually typing
            results['keyboard_simulation'] = True
        except:
            pass
            
        # Test active app detection
        try:
            app_info = self.smart_inserter.accessibility_inserter.get_active_application_info()
            results['active_app_detected'] = bool(app_info.get('name'))
        except:
            pass
            
        return results
```

## Key Implementation Notes

1. **Permission Requirements**: Requires accessibility permissions for some methods
2. **Clipboard Reliability**: Clipboard method most reliable across different apps
3. **App-Specific Handling**: Different apps may need different insertion strategies
4. **Text Processing**: Format transcribed text appropriately before insertion
5. **Error Recovery**: Implement fallback methods for robustness
6. **Timing Considerations**: Allow time for paste operations to complete
7. **Special Characters**: Handle smart quotes and special characters properly