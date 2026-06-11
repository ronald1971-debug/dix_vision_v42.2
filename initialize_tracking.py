import csv
from pathlib import Path

def initialize_tracking():
    source_index = Path(r'C:\dix_vision_v42.2\source_files_index.csv')
    tracking_file = Path(r'C:\dix_vision_v42.2\system_analysis_tracking.csv')
    
    tracking_data = []
    
    with open(source_index, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tracking_data.append({
                'file_id': row['file_id'],
                'file_path': row['file_path'],
                'directory': row['directory'],
                'file_type': row['file_type'],
                'size_bytes': row['size_bytes'],
                'analyzed': 'no',
                'summary': '',
                'issues_found': '',
                'importance': '',
                'status': 'pending'
            })
    
    # Write tracking table
    with open(tracking_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file_id', 'file_path', 'directory', 'file_type', 'size_bytes', 'analyzed', 'summary', 'issues_found', 'importance', 'status'])
        writer.writeheader()
        writer.writerows(tracking_data)
    
    print(f"Tracking table initialized with {len(tracking_data)} files")
    print(f"Tracking table written to: {tracking_file}")
    
    return tracking_data

if __name__ == "__main__":
    initialize_tracking()
