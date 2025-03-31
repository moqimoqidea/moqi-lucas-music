#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import subprocess
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Video file extensions to convert
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

def create_output_directory(source_dir):
    """
    Create output directory with name 'source_dir_name + audio'.
    If directory exists, add timestamp.
    """
    source_path = Path(source_dir)
    parent_dir = source_path.parent
    base_name = f"{source_path.name}_audio"
    
    output_dir = parent_dir / base_name
    
    # If output directory already exists, add timestamp
    if output_dir.exists():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{base_name}_{timestamp}"
        output_dir = parent_dir / base_name
        
    # Create the output directory
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    
    return output_dir

def recreate_directory_structure(source_dir, output_dir):
    """
    Recursively recreate directory structure from source_dir to output_dir
    """
    source_path = Path(source_dir)
    
    for dirpath, dirnames, _ in os.walk(source_path):
        # Get relative path from source_dir
        rel_path = Path(dirpath).relative_to(source_path)
        
        # Create corresponding directory in output_dir
        if str(rel_path) != '.':  # Skip root directory
            target_dir = output_dir / rel_path
            target_dir.mkdir(exist_ok=True)
            logger.info(f"Created directory: {target_dir}")
    
    logger.info("Directory structure recreation completed")

def convert_video_to_audio(video_path, audio_path):
    """
    Convert video file to audio file using ffmpeg
    """
    try:
        # Use ffmpeg to convert video to audio
        cmd = [
            'ffmpeg', 
            '-i', str(video_path), 
            '-q:a', '0',  # Best quality
            '-map', 'a',  # Extract audio only
            '-y',  # Overwrite output file if exists
            str(audio_path)
        ]
        
        logger.info(f"Converting: {video_path} -> {audio_path}")
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Conversion failed: {result.stderr}")
            return False
        
        logger.info(f"Conversion successful: {audio_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        return False

def process_videos(source_dir, output_dir):
    """
    Recursively process all video files in source_dir
    """
    source_path = Path(source_dir)
    total_videos = 0
    successful_conversions = 0
    
    for dirpath, _, filenames in os.walk(source_path):
        rel_path = Path(dirpath).relative_to(source_path)
        target_dir = output_dir / rel_path
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            file_ext = file_path.suffix.lower()
            
            if file_ext in VIDEO_EXTENSIONS:
                total_videos += 1
                
                # Create output audio file path with .mp3 extension
                audio_filename = f"{file_path.stem}.mp3"
                audio_path = target_dir / audio_filename
                
                # Convert video to audio
                if convert_video_to_audio(file_path, audio_path):
                    successful_conversions += 1
    
    logger.info(f"Processing completed. Total videos: {total_videos}, Successfully converted: {successful_conversions}")

def main():
    """
    Main function to process command line arguments and start conversion
    """
    if len(sys.argv) != 2:
        logger.error("Usage: python video_to_audio.py <source_directory>")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        sys.exit(1)
    
    logger.info(f"Starting video to audio conversion from: {source_dir}")
    
    # Create output directory
    output_dir = create_output_directory(source_dir)
    
    # Recreate directory structure
    recreate_directory_structure(source_dir, output_dir)
    
    # Process videos
    process_videos(source_dir, output_dir)
    
    logger.info("All operations completed successfully")

if __name__ == "__main__":
    main()