"""
Generate Pre-recorded Audio Files
Run this script once to generate all pre-recorded audio files
"""
import os
from tts_service import tts_with_fallback
from prerecorded_audio import get_all_phrases, PRERECORDED_DIR
import shutil

def generate_all_prerecorded_audio():
    """Generate all pre-recorded audio files"""
    print("=" * 70)
    print("GENERATING PRE-RECORDED AUDIO FILES")
    print("=" * 70)
    print()
    
    # Get all phrases
    phrases = get_all_phrases()
    
    total = len(phrases)
    success = 0
    failed = 0
    
    for idx, (key, data) in enumerate(phrases.items(), 1):
        text = data["text"]
        file_path = data["file"]
        full_path = os.path.join(PRERECORDED_DIR, file_path)
        
        print(f"[{idx}/{total}] Generating: {key}")
        print(f"  Text: \"{text}\"")
        print(f"  File: {file_path}")
        
        # Check if already exists
        if os.path.exists(full_path):
            print(f"  ⚠️  Already exists, skipping...")
            success += 1
            print()
            continue
        
        # Generate TTS
        try:
            result = tts_with_fallback(
                text=text,
                session_id="prerecorded",
                segment_id=key
            )
            
            if result['status'] == 'success':
                # Copy to prerecorded directory
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                shutil.copy2(result['output_path'], full_path)
                print(f"  ✅ Generated successfully!")
                success += 1
            else:
                print(f"  ❌ Failed: {result.get('error_message', 'Unknown error')}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"✅ Success: {success}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print()
    print(f"Audio files saved to: {PRERECORDED_DIR}")
    print()
    
    if failed == 0:
        print("🎉 All pre-recorded audio files generated successfully!")
    else:
        print("⚠️  Some files failed to generate. Check the errors above.")


if __name__ == "__main__":
    generate_all_prerecorded_audio()
