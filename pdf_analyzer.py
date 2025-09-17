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
                'images': []
            }
            
            image_count = 0
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    image_count += 1
                    
                    # Extract image data
                    xref = img[0]  # Image reference number
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Get image properties
                    img_data = self._analyze_image(doc, xref, pix, page_num + 1, image_count)
                    
                    if img_data:
                        result['images'].append(img_data)
                    
                    # Clean up pixmap
                    pix = None
            
            result['total_images'] = len(result['images'])
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
    
    def _analyze_image(self, doc, xref, pix, page_num, img_number):
        """Analyze individual image properties"""
        try:
            img_data = {
                'page': page_num,
                'image_number': img_number,
                'xref': xref,
                'width': pix.width,
                'height': pix.height,
                'channels': pix.n,
                'format': None,
                'color_mode': self._get_color_mode(pix),
                'dpi': None,
                'bit_depth': None,
                'file_size': 0,
                'preview_base64': None,
                'dpi_method': 'estimated',
                'pixel_density': (pix.width * pix.height) / 1000000.0,  # Megapixels
                'original_colorspace': None,
                'error': None
            }
            
            # Try to get original image data from PDF
            try:
                img_dict = doc.extract_image(xref)
                img_data['file_size'] = len(img_dict['image'])
                img_data['format'] = img_dict['ext'].upper()
                
                # Try to get DPI from original image
                if img_dict['ext'] in ['jpg', 'jpeg', 'png', 'tiff']:
                    dpi = self._extract_dpi_from_image_data(img_dict['image'], img_dict['ext'])
                    if dpi:
                        img_data['dpi'] = dpi
                        img_data['dpi_method'] = 'extracted'
                
            except Exception as e:
                self.logger.warning(f"Could not extract original image data: {str(e)}")
            
            # Estimate DPI if not found
            if not img_data['dpi']:
                img_data['dpi'] = self._estimate_dpi(pix.width, pix.height)
                img_data['dpi_method'] = 'estimated'
            
            # Get bit depth
            img_data['bit_depth'] = 8  # Most common, could be refined
            
            # Generate preview
            try:
                img_data['preview_base64'] = self._create_preview(pix)
            except Exception as e:
                self.logger.warning(f"Could not create preview: {str(e)}")
            
            return img_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing image {img_number}: {str(e)}")
            return {
                'page': page_num,
                'image_number': img_number,
                'error': str(e),
                'width': 0,
                'height': 0,
                'dpi': None,
                'color_mode': 'Unknown',
                'file_size': 0
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