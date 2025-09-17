import fitz  # PyMuPDF
import io
import base64
from PIL import Image
import logging
import struct

class PDFAnalyzer:
    """PDF analysis class for extracting and analyzing images from PDF files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_pdf(self, pdf_data):
        """Analyze a PDF file and extract image information"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            result = {
                'error': None,
                'total_pages': len(doc),
                'total_images': 0,
                'total_placements': 0,
                'unique_images': 0,
                'images': []
            }
            
            placement_count = 0
            processed_xrefs = set()
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                # Process each unique image on this page
                for img_index, img in enumerate(image_list):
                    xref = img[0]  # Image reference number
                    
                    # Track unique images
                    if xref not in processed_xrefs:
                        processed_xrefs.add(xref)
                    
                    # Get all placement rectangles for this image on this page
                    try:
                        rects = page.get_image_rects(xref)
                        if not rects:
                            # Skip if no placement rects found - can't calculate visible DPI
                            self.logger.warning(f"No placement rectangles found for xref {xref} on page {page_num + 1}")
                            continue
                    except Exception as e:
                        self.logger.warning(f"Could not get image rects for xref {xref}: {str(e)}")
                        continue
                    
                    # Create pixmap once per xref for efficiency
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Process each placement of this image
                    for placement_index, rect in enumerate(rects):
                        placement_count += 1
                        
                        # Get image properties with placement information
                        img_data = self._analyze_image_placement(
                            doc, xref, pix, page_num + 1, placement_count, 
                            rect, placement_index + 1, len(rects)
                        )
                        
                        if img_data:
                            result['images'].append(img_data)
                    
                    # Clean up pixmap
                    pix = None
            
            result['total_images'] = len(result['images'])  # Total placements
            result['total_placements'] = len(result['images'])
            result['unique_images'] = len(processed_xrefs)
            doc.close()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing PDF: {str(e)}")
            return {
                'error': str(e),
                'total_pages': 0,
                'total_images': 0,
                'images': []
            }
    
    def _analyze_image_placement(self, doc, xref, pix, page_num, placement_number, rect, placement_index, total_placements):
        """Analyze individual image placement properties including visible DPI"""
        try:
            # Calculate placement dimensions in inches (PDF points to inches: 1 inch = 72 points)
            placed_width_in = rect.width / 72.0 if rect.width > 0 else None
            placed_height_in = rect.height / 72.0 if rect.height > 0 else None
            
            # Calculate effective DPI based on actual placement
            if placed_width_in and placed_height_in and placed_width_in > 0 and placed_height_in > 0:
                eff_ppi_x = pix.width / placed_width_in
                eff_ppi_y = pix.height / placed_height_in
                visible_dpi = min(eff_ppi_x, eff_ppi_y)  # Use the limiting dimension
            else:
                eff_ppi_x = None
                eff_ppi_y = None
                visible_dpi = None
            
            img_data = {
                'page': page_num,
                'image_number': placement_number,
                'placement_index': placement_index,
                'total_placements_of_image': total_placements,
                'xref': xref,
                'width': pix.width,  # Native pixel width
                'height': pix.height,  # Native pixel height
                'placed_width_in': round(placed_width_in, 3) if placed_width_in else None,
                'placed_height_in': round(placed_height_in, 3) if placed_height_in else None,
                'placed_width_points': round(rect.width, 1),
                'placed_height_points': round(rect.height, 1),
                'eff_ppi_x': round(eff_ppi_x, 1) if eff_ppi_x else None,
                'eff_ppi_y': round(eff_ppi_y, 1) if eff_ppi_y else None,
                'visible_dpi': round(visible_dpi, 1) if visible_dpi else None,
                'channels': pix.n,
                'format': None,
                'color_mode': self._get_color_mode(pix),
                'metadata_dpi': None,  # Original embedded DPI
                'bit_depth': None,
                'file_size': 0,
                'preview_base64': None,
                'dpi_method': 'visible_calculated',
                'pixel_density': (pix.width * pix.height) / 1000000.0,  # Megapixels
                'original_colorspace': None,
                'placement_rect': {
                    'x0': round(rect.x0, 1),
                    'y0': round(rect.y0, 1), 
                    'x1': round(rect.x1, 1),
                    'y1': round(rect.y1, 1)
                },
                'error': None
            }
            
            # Try to get original image data from PDF
            try:
                img_dict = doc.extract_image(xref)
                img_data['file_size'] = len(img_dict['image'])
                img_data['format'] = img_dict['ext'].upper()
                
                # Try to get metadata DPI from original image
                if img_dict['ext'] in ['jpg', 'jpeg', 'png', 'tiff']:
                    metadata_dpi = self._extract_dpi_from_image_data(img_dict['image'], img_dict['ext'])
                    if metadata_dpi:
                        img_data['metadata_dpi'] = metadata_dpi
                        img_data['dpi_method'] = 'visible_calculated + metadata_extracted'
                
            except Exception as e:
                self.logger.warning(f"Could not extract original image data: {str(e)}")
            
            # Estimate metadata DPI if not found (keep for reference)
            if not img_data['metadata_dpi']:
                img_data['metadata_dpi'] = self._estimate_dpi(pix.width, pix.height)
            
            # Get bit depth
            img_data['bit_depth'] = 8  # Most common, could be refined
            
            # Generate preview
            try:
                img_data['preview_base64'] = self._create_preview(pix)
            except Exception as e:
                self.logger.warning(f"Could not create preview: {str(e)}")
            
            return img_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing image placement {placement_number}: {str(e)}")
            return {
                'page': page_num,
                'image_number': placement_number,
                'placement_index': placement_index,
                'error': str(e),
                'width': 0,
                'height': 0,
                'visible_dpi': 0,
                'metadata_dpi': None,
                'color_mode': 'Unknown',
                'file_size': 0,
                'placed_width_in': 0,
                'placed_height_in': 0
            }
    
    def _get_color_mode(self, pix):
        """Determine color mode from pixmap"""
        if pix.n == 1:
            return "Grayscale"
        elif pix.n == 3:
            return "RGB"
        elif pix.n == 4:
            if pix.alpha:
                return "RGBA"
            else:
                return "CMYK"
        elif pix.n == 2:
            return "Grayscale + Alpha"
        else:
            return f"{pix.n}-channel"
    
    def _estimate_dpi(self, width, height):
        """Estimate DPI based on image dimensions"""
        # Common print sizes and their typical dimensions
        # This is a rough estimation
        
        pixel_count = width * height
        
        # High resolution indicators
        if pixel_count > 6000000:  # > 6MP
            return 300
        elif pixel_count > 2000000:  # > 2MP
            return 240
        elif pixel_count > 1000000:  # > 1MP
            return 180
        elif pixel_count > 500000:   # > 0.5MP
            return 150
        else:
            return 72
    
    def _extract_dpi_from_image_data(self, image_data, format):
        """Extract DPI from image metadata"""
        try:
            if format.lower() in ['jpg', 'jpeg']:
                return self._extract_jpeg_dpi(image_data)
            elif format.lower() == 'png':
                return self._extract_png_dpi(image_data)
            elif format.lower() in ['tif', 'tiff']:
                return self._extract_tiff_dpi(image_data)
        except Exception as e:
            self.logger.debug(f"Could not extract DPI from {format}: {str(e)}")
        
        return None
    
    def _extract_jpeg_dpi(self, image_data):
        """Extract DPI from JPEG EXIF data"""
        try:
            # Look for JFIF header
            pos = image_data.find(b'JFIF')
            if pos != -1:
                # JFIF density info starts 5 bytes after "JFIF"
                density_pos = pos + 7
                if density_pos + 4 < len(image_data):
                    units = image_data[density_pos]
                    x_density = struct.unpack('>H', image_data[density_pos+1:density_pos+3])[0]
                    
                    if units == 1:  # DPI
                        return x_density
                    elif units == 2:  # DPC (dots per cm)
                        return int(x_density * 2.54)
        except:
            pass
        return None
    
    def _extract_png_dpi(self, image_data):
        """Extract DPI from PNG pHYs chunk"""
        try:
            # Look for pHYs chunk
            pos = image_data.find(b'pHYs')
            if pos != -1:
                # pHYs data starts 4 bytes after chunk name
                data_pos = pos + 4
                if data_pos + 8 < len(image_data):
                    x_pixels_per_unit = struct.unpack('>I', image_data[data_pos:data_pos+4])[0]
                    unit_specifier = image_data[data_pos+8]
                    
                    if unit_specifier == 1:  # meters
                        return int(x_pixels_per_unit / 39.3701)  # Convert to DPI
        except:
            pass
        return None
    
    def _extract_tiff_dpi(self, image_data):
        """Extract DPI from TIFF metadata"""
        try:
            # Basic TIFF DPI extraction would be complex
            # For now, return None and use estimation
            pass
        except:
            pass
        return None
    
    def _create_preview(self, pix):
        """Create base64 encoded preview image"""
        try:
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Resize for preview (max 200x200)
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            self.logger.warning(f"Could not create preview: {str(e)}")
            return None