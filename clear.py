import shutil
import os

# CONFIGURATION
folder_to_clear = "sorted"

def clear_folder():
    # 1. Check if folder exists
    if os.path.exists(folder_to_clear):
        try:
            shutil.rmtree(folder_to_clear)
            print(" -> Deleted successfully.")
        except Exception as e:
            print(f"   -> ❌ Error deleting folder: {e}")
            return
    else:
        print(f"ℹ️  '{folder_to_clear}' does not exist yet.")

    # 3. Recreate the empty folder
    try:
        os.makedirs(folder_to_clear)
        print(f"✅ Created fresh '{folder_to_clear}' folder.")
    except Exception as e:
        print(f"   -> ❌ Error creating folder: {e}")

# Run the function
if __name__ == "__main__":
    confirm = "y"
    if confirm.lower() == "y":
        clear_folder()
    else:
        print("Operation cancelled.")