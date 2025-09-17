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
        # Extract image properties
        page = img.get('page', 'Unknown')
        width = img.get('width', 0)
        height = img.get('height', 0)
        dpi = img.get('dpi', 0)
        color_mode = img.get('color_mode', 'Unknown')
        file_size = img.get('file_size', 0)
        format_type = img.get('format', 'Unknown')
        
        # Calculate print dimensions
        if width and height and dpi:
            print_width = width / dpi
            print_height = height / dpi
            print_size = f"{print_width:.2f}\" × {print_height:.2f}\""
        else:
            print_size = "Unknown"
        
        # Determine status
        dpi_status = "PASS" if dpi and dpi >= min_dpi else "FAIL"
        color_status = "PASS" if color_mode in preferred_modes else "FAIL"
        overall_status = "PASS" if dpi_status == "PASS" and color_status == "PASS" else "FAIL"
        
        # Quality category
        if dpi and dpi >= 300:
            quality = "Excellent"
        elif dpi and dpi >= 250:
            quality = "Good"
        elif dpi and dpi >= 150:
            quality = "Acceptable"
        else:
            quality = "Poor"
        
        data.append({
            'Image #': i,
            'Page': page,
            'Dimensions (px)': f"{width} × {height}" if width and height else "Unknown",
            'DPI': dpi if dpi else "Unknown",
            'Color Space': color_mode,
            'Format': format_type,
            'File Size': format_file_size(file_size),
            'Print Size': print_size,
            'Quality': quality,
            'DPI Status': dpi_status,
            'Color Space Status': color_status,
            'Overall Status': overall_status
        })
    
    return pd.DataFrame(data)

def get_quality_summary(images, min_dpi, preferred_modes):
    """Get summary statistics about image quality"""
    if not images:
        return {
            'total_images': 0,
            'pass_count': 0,
            'fail_count': 0,
            'pass_rate': 0,
            'high_quality_count': 0,
            'average_dpi': 0
        }
    
    total_images = len(images)
    pass_count = 0
    high_quality_count = 0
    dpi_values = []
    
    for img in images:
        dpi = img.get('dpi', 0)
        color_mode = img.get('color_mode', '')
        
        # Collect DPI values for average calculation
        if dpi:
            dpi_values.append(dpi)
        
        # Check if image passes criteria
        dpi_pass = dpi and dpi >= min_dpi
        color_pass = color_mode in preferred_modes
        
        if dpi_pass and color_pass:
            pass_count += 1
        
        if dpi and dpi >= 300:
            high_quality_count += 1
    
    average_dpi = sum(dpi_values) / len(dpi_values) if dpi_values else 0
    pass_rate = (pass_count / total_images * 100) if total_images > 0 else 0
    
    return {
        'total_images': total_images,
        'pass_count': pass_count,
        'fail_count': total_images - pass_count,
        'pass_rate': pass_rate,
        'high_quality_count': high_quality_count,
        'average_dpi': average_dpi
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
    """Validate PDF images for print quality"""
    if preferred_modes is None:
        preferred_modes = ["CMYK", "Grayscale"]
    
    issues = []
    recommendations = []
    
    if not images:
        issues.append("No images found in PDF")
        recommendations.append("Ensure the PDF contains embedded images")
        return issues, recommendations
    
    # Check for low DPI images
    low_dpi_images = [img for img in images if img.get('dpi') and img['dpi'] < min_dpi]
    if low_dpi_images:
        issues.append(f"{len(low_dpi_images)} image(s) have DPI below {min_dpi}")
        recommendations.append(f"Increase image resolution to at least {min_dpi} DPI")
    
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
    corrupted_images = [img for img in images if img.get('error') or not img.get('dpi') or not img.get('color_mode')]
    if corrupted_images:
        issues.append(f"{len(corrupted_images)} image(s) could not be fully analyzed")
        recommendations.append("Check for corrupted or improperly embedded images")
    
    return issues, recommendations