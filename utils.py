import pandas as pd

def format_file_size(size_bytes):
    """Convert bytes to human readable file size"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_bytes = float(size_bytes)
    i = 0
    
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    if i == 0:
        return f"{int(size_bytes)} {size_names[i]}"
    else:
        return f"{size_bytes:.1f} {size_names[i]}"

def create_results_dataframe(images, min_dpi, preferred_modes):
    """Create a pandas DataFrame with analysis results"""
    if not images:
        return pd.DataFrame()
    
    data = []
    
    for i, img in enumerate(images, 1):
        # Extract image properties with new visible DPI structure
        page = img.get('page', 'Unknown')
        width = img.get('width', 0)
        height = img.get('height', 0)
        visible_dpi = img.get('visible_dpi', 0)
        metadata_dpi = img.get('metadata_dpi', 0)
        color_mode = img.get('color_mode', 'Unknown')
        file_size = img.get('file_size', 0)
        format_type = img.get('format', 'Unknown')
        placed_width_in = img.get('placed_width_in', 0)
        placed_height_in = img.get('placed_height_in', 0)
        
        # Handle placement information
        placement_info = ""
        if img.get('placement_index') and img.get('total_placements_of_image'):
            if img['total_placements_of_image'] > 1:
                placement_info = f" ({img['placement_index']}/{img['total_placements_of_image']})"
        
        # Placed size display
        placed_size = f"{placed_width_in:.2f}\" × {placed_height_in:.2f}\"" if placed_width_in and placed_height_in else "Unknown"
        
        # Determine status based on VISIBLE DPI (not metadata DPI)
        dpi_status = "PASS" if visible_dpi and visible_dpi >= min_dpi else "FAIL"
        color_status = "PASS" if color_mode in preferred_modes else "FAIL"
        overall_status = "PASS" if dpi_status == "PASS" and color_status == "PASS" else "FAIL"
        
        # Quality category based on visible DPI
        if visible_dpi and visible_dpi >= 300:
            quality = "Excellent"
        elif visible_dpi and visible_dpi >= 250:
            quality = "Good"
        elif visible_dpi and visible_dpi >= 150:
            quality = "Acceptable"
        else:
            quality = "Poor"
        
        data.append({
            'Image #': f"{img.get('image_number', i)}{placement_info}",
            'Page': page,
            'Native Size (px)': f"{width} × {height}" if width and height else "Unknown",
            'Placed Size': placed_size,
            'Visible DPI': f"{visible_dpi:.0f}" if visible_dpi else "Unknown",
            'Metadata DPI': f"{metadata_dpi:.0f}" if metadata_dpi else "Unknown",
            'Color Space': color_mode,
            'Format': format_type,
            'File Size': format_file_size(file_size),
            'Quality': quality,
            'DPI Status': dpi_status,
            'Color Space Status': color_status,
            'Overall Status': overall_status
        })
    
    return pd.DataFrame(data)

def get_quality_summary(images, min_dpi, preferred_modes):
    """Get summary statistics about image quality based on visible DPI"""
    if not images:
        return {
            'total_images': 0,
            'pass_count': 0,
            'fail_count': 0,
            'pass_rate': 0,
            'high_quality_count': 0,
            'average_visible_dpi': 0,
            'average_metadata_dpi': 0
        }
    
    total_images = len(images)
    pass_count = 0
    high_quality_count = 0
    visible_dpi_values = []
    metadata_dpi_values = []
    
    for img in images:
        visible_dpi = img.get('visible_dpi', 0)
        metadata_dpi = img.get('metadata_dpi', 0)
        color_mode = img.get('color_mode', '')
        
        # Collect DPI values for average calculation
        if visible_dpi:
            visible_dpi_values.append(visible_dpi)
        if metadata_dpi:
            metadata_dpi_values.append(metadata_dpi)
        
        # Check if image passes criteria based on VISIBLE DPI
        dpi_pass = visible_dpi and visible_dpi >= min_dpi
        color_pass = color_mode in preferred_modes
        
        if dpi_pass and color_pass:
            pass_count += 1
        
        if visible_dpi and visible_dpi >= 300:
            high_quality_count += 1
    
    average_visible_dpi = sum(visible_dpi_values) / len(visible_dpi_values) if visible_dpi_values else 0
    average_metadata_dpi = sum(metadata_dpi_values) / len(metadata_dpi_values) if metadata_dpi_values else 0
    pass_rate = (pass_count / total_images * 100) if total_images > 0 else 0
    
    return {
        'total_images': total_images,
        'pass_count': pass_count,
        'fail_count': total_images - pass_count,
        'pass_rate': pass_rate,
        'high_quality_count': high_quality_count,
        'average_visible_dpi': average_visible_dpi,
        'average_metadata_dpi': average_metadata_dpi
    }

def get_color_space_distribution(images):
    """Get distribution of color spaces in images"""
    color_counts = {}
    
    for img in images:
        color_mode = img.get('color_mode', 'Unknown')
        color_counts[color_mode] = color_counts.get(color_mode, 0) + 1
    
    total = len(images)
    distribution = {}
    
    for color_mode, count in color_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        distribution[color_mode] = {
            'count': count,
            'percentage': percentage
        }
    
    return distribution

def validate_pdf_for_print(images, min_dpi=300, preferred_modes=None):
    """Validate PDF images for print quality based on visible DPI"""
    if preferred_modes is None:
        preferred_modes = ["CMYK", "Grayscale"]
    
    issues = []
    recommendations = []
    
    if not images:
        issues.append("No images found in PDF")
        recommendations.append("Ensure the PDF contains embedded images")
        return issues, recommendations
    
    # Check for low VISIBLE DPI images (this is what matters for print quality)
    low_dpi_images = [img for img in images if img.get('visible_dpi') and img['visible_dpi'] < min_dpi]
    if low_dpi_images:
        issues.append(f"{len(low_dpi_images)} image placement(s) have visible DPI below {min_dpi}")
        recommendations.append(f"Increase image size in the document or use higher resolution images to achieve at least {min_dpi} visible DPI")
    
    # Check for images that are scaled too large (low visible DPI due to scaling)
    over_scaled_images = [img for img in images 
                         if img.get('visible_dpi') and img.get('metadata_dpi') 
                         and img['visible_dpi'] < img['metadata_dpi'] * 0.7]  # Scaled up significantly
    if over_scaled_images:
        issues.append(f"{len(over_scaled_images)} image(s) are scaled larger than recommended")
        recommendations.append("Consider using higher resolution source images or reducing the placed size in the document")
    
    # Check color spaces
    wrong_color_images = [img for img in images if img.get('color_mode') and img['color_mode'] not in preferred_modes]
    if wrong_color_images:
        color_modes = set(img['color_mode'] for img in wrong_color_images)
        issues.append(f"{len(wrong_color_images)} image(s) use non-preferred color spaces: {', '.join(color_modes)}")
        recommendations.append(f"Convert images to preferred color spaces: {', '.join(preferred_modes)}")
    
    # Check for very large images that might cause printing issues
    large_images = [img for img in images if img.get('width', 0) * img.get('height', 0) > 10000000]  # > 10MP
    if large_images:
        issues.append(f"{len(large_images)} image(s) are very large and may cause printing delays")
        recommendations.append("Consider optimizing very large images for print workflow")
    
    # Check for corrupted or unreadable images
    corrupted_images = [img for img in images if img.get('error') or not img.get('visible_dpi') or not img.get('color_mode')]
    if corrupted_images:
        issues.append(f"{len(corrupted_images)} image(s) could not be fully analyzed")
        recommendations.append("Check for corrupted or improperly embedded images")
    
    return issues, recommendations