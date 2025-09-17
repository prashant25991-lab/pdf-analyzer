import streamlit as st
import pandas as pd
import io
import base64
from pdf_analyzer import PDFAnalyzer
from utils import format_file_size, create_results_dataframe

def main():
    st.set_page_config(
        page_title="PDF Preflight Tool",
        page_icon="📄",
        layout="wide"
    )
    
    # Custom CSS for better design
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 1.5rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            background: linear-gradient(145deg, #f8f9fa, #e9ecef);
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: linear-gradient(145deg, #e9ecef, #f8f9fa);
        }
        
        .metric-card {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 0.8rem 0;
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .status-pass {
            color: #28a745;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .status-fail {
            color: #dc3545;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .image-card {
            border: 1px solid #e0e6ed;
            border-radius: 12px;
            padding: 1.2rem;
            background: white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .image-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .sidebar-section {
            background: linear-gradient(145deg, #f8f9fa, #ffffff);
            padding: 1.2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 1px solid #e9ecef;
        }
        
        .help-text {
            font-size: 0.85em;
            color: #6c757d;
            font-style: italic;
            margin-top: 0.5rem;
        }
        
        .summary-stats {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
        }
        
        .quality-indicator {
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin: 0.2rem;
        }
        
        .quality-excellent { background-color: #28a745; color: white; }
        .quality-good { background-color: #20c997; color: white; }
        .quality-acceptable { background-color: #ffc107; color: black; }
        .quality-poor { background-color: #dc3545; color: white; }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem;">📄 PDF Preflight Tool</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Professional print quality analysis for PDF files
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h2 style="margin-top: 0; color: #667eea;">⚙️ Preflight Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # DPI thresholds
        with st.container():
            st.markdown("""
            <div class="sidebar-section">
                <h3 style="margin-top: 0; color: #495057;">📊 Quality Thresholds</h3>
            </div>
            """, unsafe_allow_html=True)
            
            min_dpi = st.number_input(
                "Minimum DPI", 
                min_value=72, 
                max_value=600, 
                value=300,
                help="Minimum DPI required for print quality (typically 300 for high-quality print)"
            )
            st.markdown('<p class="help-text">Professional print: 300+ DPI</p>', unsafe_allow_html=True)
            
            max_file_size = st.number_input(
                "Max File Size (MB)", 
                min_value=1, 
                max_value=100, 
                value=50,
                help="Maximum allowed file size for analysis"
            )
        
        # Color space preferences
        with st.container():
            st.markdown("""
            <div class="sidebar-section">
                <h3 style="margin-top: 0; color: #495057;">🎨 Color Space Settings</h3>
            </div>
            """, unsafe_allow_html=True)
            
            preferred_modes = st.multiselect(
                "Acceptable Color Spaces",
                ["RGB", "CMYK", "Grayscale", "1-bit"],
                default=["CMYK", "Grayscale"],
                help="Choose which color spaces are acceptable for your print workflow"
            )
            st.markdown('<p class="help-text">CMYK recommended for print, RGB for digital</p>', unsafe_allow_html=True)
        
        # Quick reference
        with st.container():
            st.markdown("""
            <div class="sidebar-section">
                <h3 style="margin-top: 0; color: #495057;">📖 Quick Reference</h3>
                <div style="font-size: 0.9em;">
                    <p><strong>DPI Guidelines:</strong></p>
                    <ul style="margin: 0.5rem 0;">
                        <li>300+ DPI: Professional print</li>
                        <li>150-299 DPI: Basic print</li>
                        <li>72-149 DPI: Screen only</li>
                    </ul>
                    <p><strong>Color Spaces:</strong></p>
                    <ul style="margin: 0.5rem 0;">
                        <li>CMYK: Commercial printing</li>
                        <li>RGB: Digital displays</li>
                        <li>Grayscale: Black & white print</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="upload-area">
            <h2 style="margin-top: 0; color: #667eea;">📤 Upload PDF Files</h2>
            <p style="color: #6c757d; margin-bottom: 1rem;">
                Drop your PDF files here or click to browse<br>
                <small>Supports multiple file selection</small>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            help="Upload one or more PDF files to analyze their DPI, resolution, and color space",
            label_visibility="collapsed",
            accept_multiple_files=True
        )
        
        if uploaded_files:
            total_size = sum(len(file.getvalue()) for file in uploaded_files)
            
            # Files info card
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #495057;">📄 {len(uploaded_files)} PDF file(s) selected</h4>
                <p style="margin: 0; color: #6c757d;">
                    Total Size: {format_file_size(total_size)}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check individual file sizes
            oversized_files = []
            for file in uploaded_files:
                file_size = len(file.getvalue())
                if file_size > max_file_size * 1024 * 1024:
                    oversized_files.append(file.name)
            
            if oversized_files:
                st.error(f"❌ Files exceed maximum limit of {max_file_size}MB: {', '.join(oversized_files)}")
                return
            
            # Show file list
            with st.expander(f"📋 File List ({len(uploaded_files)} files)", expanded=False):
                for i, file in enumerate(uploaded_files, 1):
                    file_size = len(file.getvalue())
                    st.text(f"{i}. {file.name} ({format_file_size(file_size)})")
            
            # Analyze button with better styling
            if st.button("🔍 Analyze PDFs", type="primary", use_container_width=True):
                analyze_multiple_pdfs(uploaded_files, min_dpi, preferred_modes, col2)
        else:
            st.markdown("""
            <div class="metric-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #6c757d;">ℹ️ Instructions</h4>
                <ul style="margin: 0; color: #6c757d; font-size: 0.9em;">
                    <li>Upload one or more PDF files to start analysis</li>
                    <li>Adjust quality thresholds in the sidebar</li>
                    <li>View detailed results for each file</li>
                    <li>Get print quality recommendations</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        


def analyze_pdf(uploaded_file, min_dpi, preferred_modes, display_column):
    """Analyze the uploaded PDF file"""
    with display_column:
        st.header("Analysis Results")
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize analyzer
            status_text.text("Initializing PDF analyzer...")
            progress_bar.progress(10)
            
            analyzer = PDFAnalyzer()
            
            # Load PDF
            status_text.text("Loading PDF file...")
            progress_bar.progress(20)
            
            pdf_data = uploaded_file.getvalue()
            analysis_result = analyzer.analyze_pdf(pdf_data)
            
            progress_bar.progress(50)
            status_text.text("Extracting and analyzing images...")
            
            if analysis_result['error']:
                st.error(f"Error analyzing PDF: {analysis_result['error']}")
                return
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Display results
            display_results(analysis_result, min_dpi, preferred_modes)
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
        finally:
            progress_bar.empty()
            status_text.empty()

def analyze_multiple_pdfs(uploaded_files, min_dpi, preferred_modes, display_column):
    """Analyze multiple uploaded PDF files"""
    with display_column:
        st.header("Analysis Results")
        
        # Create progress bar for overall progress
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        all_results = []
        total_files = len(uploaded_files)
        
        try:
            analyzer = PDFAnalyzer()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name} ({i+1}/{total_files})...")
                
                # Update overall progress
                file_progress = i / total_files
                overall_progress.progress(file_progress)
                
                try:
                    # Analyze individual PDF
                    pdf_data = uploaded_file.getvalue()
                    analysis_result = analyzer.analyze_pdf(pdf_data)
                    
                    if analysis_result['error']:
                        st.error(f"Error analyzing {uploaded_file.name}: {analysis_result['error']}")
                        continue
                    
                    # Add file name to results
                    analysis_result['filename'] = uploaded_file.name
                    all_results.append(analysis_result)
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    continue
            
            # Final progress update
            overall_progress.progress(1.0)
            status_text.text("Analysis complete!")
            
            if not all_results:
                st.error("No PDF files could be processed successfully.")
                return
            
            # Display combined results
            display_multiple_pdf_results(all_results, min_dpi, preferred_modes)
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
        finally:
            overall_progress.empty()
            status_text.empty()

def display_multiple_pdf_results(all_results, min_dpi, preferred_modes):
    """Display results for multiple PDF files"""
    
    # Overall summary
    total_files = len(all_results)
    total_images = sum(result['total_images'] for result in all_results)
    
    st.markdown(f"""
    <div class="summary-stats">
        <h3 style="margin: 0 0 1rem 0;">📈 Overall Summary</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="text-align: center; margin: 0.5rem;">
                <h2 style="margin: 0; font-size: 2rem;">{total_files}</h2>
                <p style="margin: 0; opacity: 0.9;">PDF Files</p>
            </div>
            <div style="text-align: center; margin: 0.5rem;">
                <h2 style="margin: 0; font-size: 2rem;">{total_images}</h2>
                <p style="margin: 0; opacity: 0.9;">Total Images</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display results for each PDF
    for i, result in enumerate(all_results):
        st.markdown(f"## 📄 {result['filename']}")
        
        # Display individual PDF results
        if result['total_images'] > 0:
            display_image_grid(result['images'], min_dpi, preferred_modes)
            
            # Individual summary table
            st.subheader("📊 Summary Table")
            df = create_results_dataframe(result['images'], min_dpi, preferred_modes)
            
            # Style the dataframe
            def style_results(val):
                if val == "PASS":
                    return 'background-color: #d4edda; color: #155724'
                elif val == "FAIL":
                    return 'background-color: #f8d7da; color: #721c24'
                return ''
            
            styled_df = df.style.map(style_results, subset=['DPI Status', 'Color Space Status', 'Overall Status'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Individual recommendations
            display_recommendations(result, min_dpi, preferred_modes)
        else:
            st.info(f"No images found in {result['filename']}")
        
        # Add separator between files (except for the last one)
        if i < len(all_results) - 1:
            st.markdown("---")

def display_results(results, min_dpi, preferred_modes):
    """Display the analysis results"""
    
    # Overall summary
    st.subheader("📊 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pages", results['total_pages'])
    
    with col2:
        st.metric("Images Found", results['total_images'])
    
    with col3:
        if results['total_images'] > 0:
            avg_dpi = sum(img['dpi'] for img in results['images'] if img['dpi']) / len([img for img in results['images'] if img['dpi']])
            st.metric("Average DPI", f"{avg_dpi:.0f}")
        else:
            st.metric("Average DPI", "N/A")
    
    with col4:
        # Overall pass/fail status
        overall_status = determine_overall_status(results, min_dpi, preferred_modes)
        status_color = "🟢" if overall_status == "PASS" else "🔴"
        st.metric("Status", f"{status_color} {overall_status}")
    
    if results['total_images'] == 0:
        st.warning("No images found in the PDF file.")
        return
    
    # Image previews and detailed analysis
    st.subheader("🔍 Image Analysis with Previews")
    
    # Display images in a grid with their analysis
    display_image_grid(results['images'], min_dpi, preferred_modes)
    
    # Detailed results table
    st.subheader("📊 Summary Table")
    
    df = create_results_dataframe(results['images'], min_dpi, preferred_modes)
    
    # Style the dataframe
    def style_results(val):
        if val == "PASS":
            return 'background-color: #d4edda; color: #155724'
        elif val == "FAIL":
            return 'background-color: #f8d7da; color: #721c24'
        return ''
    
    styled_df = df.style.map(style_results, subset=['DPI Status', 'Color Space Status', 'Overall Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Color space distribution
    st.subheader("🎨 Color Space Distribution")
    color_space_counts = {}
    for img in results['images']:
        mode = img.get('color_mode', 'Unknown')
        color_space_counts[mode] = color_space_counts.get(mode, 0) + 1
    
    if color_space_counts:
        col1, col2 = st.columns([2, 1])
        with col1:
            color_df = pd.DataFrame(list(color_space_counts.items()), columns=['Color Space', 'Count'])
            color_df = color_df.set_index('Color Space')
            st.bar_chart(color_df)
        with col2:
            st.write("**Color Space Summary:**")
            for mode, count in color_space_counts.items():
                percentage = (count / results['total_images']) * 100
                st.write(f"• {mode}: {count} ({percentage:.1f}%)")
    
    # Issues and recommendations
    display_recommendations(results, min_dpi, preferred_modes)
    


def determine_overall_status(results, min_dpi, preferred_modes):
    """Determine overall pass/fail status"""
    if results['total_images'] == 0:
        return "N/A"
    
    for img in results['images']:
        # Check DPI
        if img.get('dpi') and img['dpi'] < min_dpi:
            return "FAIL"
        
        # Check color mode
        if img.get('color_mode') and img['color_mode'] not in preferred_modes:
            return "FAIL"
    
    return "PASS"

def display_recommendations(results, min_dpi, preferred_modes):
    """Display recommendations based on analysis"""
    st.subheader("💡 Recommendations")
    
    issues = []
    recommendations = []
    
    # Check for DPI issues
    low_dpi_images = [img for img in results['images'] if img.get('dpi') and img['dpi'] < min_dpi]
    if low_dpi_images:
        issues.append(f"{len(low_dpi_images)} image(s) have DPI below {min_dpi}")
        recommendations.append("Increase image resolution or use higher quality images")
    
    # Check for color space issues
    wrong_color_images = [img for img in results['images'] if img.get('color_mode') and img['color_mode'] not in preferred_modes]
    if wrong_color_images:
        color_modes = set(img['color_mode'] for img in wrong_color_images)
        issues.append(f"{len(wrong_color_images)} image(s) use non-preferred color spaces: {', '.join(color_modes)}")
        recommendations.append(f"Convert images to preferred color spaces: {', '.join(preferred_modes)}")
    
    # Check for missing image data
    unknown_images = [img for img in results['images'] if not img.get('dpi') or not img.get('color_mode')]
    if unknown_images:
        issues.append(f"{len(unknown_images)} image(s) could not be fully analyzed")
        recommendations.append("Ensure images are properly embedded and not corrupted")
    
    if issues:
        st.error("**Issues Found:**")
        for issue in issues:
            st.write(f"• {issue}")
        
        st.info("**Recommendations:**")
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.success("✅ All images meet the specified criteria!")

def display_image_grid(images, min_dpi, preferred_modes):
    """Display images in a responsive grid layout with summary"""
    if not images:
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin: 0; color: #6c757d;">ℹ️ No images found in the PDF</h4>
            <p style="margin: 0.5rem 0 0 0; color: #6c757d;">
                This PDF doesn't contain any embedded images to analyze.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Summary statistics
    total_images = len(images)
    pass_count = 0
    high_quality_count = 0
    
    for img in images:
        dpi = img.get('dpi', 0)
        color_mode = img.get('color_mode', '')
        
        if (dpi and dpi >= min_dpi) and (color_mode in preferred_modes):
            pass_count += 1
        if dpi and dpi >= 300:
            high_quality_count += 1
    
    # Display summary
    st.markdown(f"""
    <div class="summary-stats">
        <h3 style="margin: 0 0 1rem 0;">📈 Analysis Summary</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="text-align: center; margin: 0.5rem;">
                <h2 style="margin: 0; font-size: 2rem;">{total_images}</h2>
                <p style="margin: 0; opacity: 0.9;">Total Images</p>
            </div>
            <div style="text-align: center; margin: 0.5rem;">
                <h2 style="margin: 0; font-size: 2rem;">{pass_count}</h2>
                <p style="margin: 0; opacity: 0.9;">Meeting Standards</p>
            </div>
            <div style="text-align: center; margin: 0.5rem;">
                <h2 style="margin: 0; font-size: 2rem;">{high_quality_count}</h2>
                <p style="margin: 0; opacity: 0.9;">High Quality (300+ DPI)</p>
            </div>
            <div style="text-align: center; margin: 0.5rem;">
                <h2 style="margin: 0; font-size: 2rem;">{(pass_count/total_images*100):.0f}%</h2>
                <p style="margin: 0; opacity: 0.9;">Pass Rate</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Image grid
    st.markdown("### 🖼️ Image Details")
    
    # Display images in rows of 3
    images_per_row = 3
    for i in range(0, len(images), images_per_row):
        cols = st.columns(images_per_row)
        
        for j, col in enumerate(cols):
            img_index = i + j
            if img_index < len(images):
                img_data = images[img_index]
                
                with col:
                    display_single_image(img_data, img_index + 1, min_dpi, preferred_modes)

def display_single_image(img_data, img_number, min_dpi, preferred_modes):
    """Display a single image with its analysis"""
    
    # Get status for styling
    dpi = img_data.get('dpi', 0)
    color_mode = img_data.get('color_mode', '')
    dpi_pass = dpi and dpi >= min_dpi
    color_pass = color_mode in preferred_modes
    overall_pass = dpi_pass and color_pass
    
    # Quality indicator
    if dpi and dpi >= 300:
        quality_class = "quality-excellent"
        quality_text = "Excellent"
    elif dpi and dpi >= 250:
        quality_class = "quality-good"
        quality_text = "Good"
    elif dpi and dpi >= 150:
        quality_class = "quality-acceptable"
        quality_text = "Acceptable"
    else:
        quality_class = "quality-poor"
        quality_text = "Poor"
    
    # Create image card
    page_info = f"Page {img_data.get('page', '?')}" if img_data.get('page') else "Unknown Page"
    
    st.markdown(f"""
    <div class="image-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #495057;">🖼️ Image {img_number}</h4>
            <span class="quality-indicator {quality_class}">{quality_text}</span>
        </div>
        <p style="margin: 0 0 1rem 0; color: #6c757d; font-size: 0.9em;">{page_info}</p>
    """, unsafe_allow_html=True)
    
    # Display image preview if available
    if img_data.get('preview_base64'):
        try:
            st.image(
                f"data:image/png;base64,{img_data['preview_base64']}", 
                caption=None,
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Could not display image: {str(e)}")
    else:
        st.markdown("""
        <div style="background-color: #f8f9fa; border: 1px dashed #dee2e6; 
                    border-radius: 8px; padding: 2rem; text-align: center; color: #6c757d;">
            📷 Preview not available
        </div>
        """, unsafe_allow_html=True)
        
    # Key metrics display
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin: 1rem 0;">
        <div style="background-color: #f8f9fa; padding: 0.5rem; border-radius: 6px; text-align: center;">
            <div style="font-weight: bold; color: {'#28a745' if dpi_pass else '#dc3545'};">
                {dpi if dpi else 'Unknown'} DPI
            </div>
            <div style="font-size: 0.8em; color: #6c757d;">Resolution</div>
        </div>
        <div style="background-color: #f8f9fa; padding: 0.5rem; border-radius: 6px; text-align: center;">
            <div style="font-weight: bold; color: {'#28a745' if color_pass else '#dc3545'};">
                {color_mode or 'Unknown'}
            </div>
            <div style="font-size: 0.8em; color: #6c757d;">Color Space</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dimensions and print size
    width = img_data.get('width', 0)
    height = img_data.get('height', 0)
    dimensions = f"{width} × {height}" if width and height else "Unknown"
    
    if width and height and dpi:
        print_width = width / dpi
        print_height = height / dpi
        print_size = f"{print_width:.2f}\" × {print_height:.2f}\""
    else:
        print_size = "Unknown"
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <p style="margin: 0.2rem 0; font-size: 0.9em; color: #495057;">
            <strong>Dimensions:</strong> {dimensions} pixels
        </p>
        <p style="margin: 0.2rem 0; font-size: 0.9em; color: #495057;">
            <strong>Print Size:</strong> {print_size}
        </p>
        <p style="margin: 0.2rem 0; font-size: 0.9em; color: #495057;">
            <strong>File Size:</strong> {format_file_size(img_data.get('file_size', 0))}
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Technical details in expander
    with st.expander("🔧 Technical Details", expanded=False):
        st.text(f"Format: {img_data.get('format', 'Unknown')}")
        if img_data.get('channels'):
            st.text(f"Channels: {img_data['channels']}")
        if img_data.get('bit_depth'):
            st.text(f"Bit Depth: {img_data['bit_depth']}")
        if img_data.get('pixel_density'):
            st.text(f"Pixel Density: {img_data['pixel_density']:.1f} MP")
        if img_data.get('original_colorspace'):
            st.text(f"Original PDF Colorspace: {img_data['original_colorspace']}")
        if img_data.get('dpi_method'):
            st.text(f"DPI Method: {img_data['dpi_method']}")
        if img_data.get('error'):
            st.error(f"Error: {img_data['error']}")



if __name__ == "__main__":
    main()