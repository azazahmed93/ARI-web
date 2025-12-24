"""
S3 Export Service - Handles PPTX upload to S3 and Lambda stitching.

This service manages the full export pipeline:
1. Generate export ID
2. Upload PPTX to S3 via presigned URL
3. Invoke stitch Lambda
4. Return download URL
"""
import os
import uuid
import json
import logging
import requests
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')

# API Configuration
API_BASE_URL = os.environ.get(
    'PPTX_EXPORT_API_URL',
    'https://pcvg9kjrfl.execute-api.us-west-2.amazonaws.com/prod'
)
S3_BUCKET = os.environ.get('PPTX_EXPORT_BUCKET', 'ari-exports-prod')

# Timeouts
PRESIGNED_URL_TIMEOUT = 30  # seconds
UPLOAD_TIMEOUT = 120  # seconds (for large files)
STITCH_TIMEOUT = 300  # seconds (Lambda can take up to 15 min)


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    export_id: str
    download_url: Optional[str] = None
    s3_key: Optional[str] = None
    error: Optional[str] = None
    components_included: Optional[List[str]] = None


class S3ExportService:
    """
    Service for uploading PPTX to S3 and orchestrating the stitch process.

    Usage:
        service = S3ExportService()
        result = service.export_and_stitch(
            session_state=dict(st.session_state),
            brand_name="MyBrand",
            industry="Tech",
            components=['streamlit_complete', 'cultural_moments']
        )
        if result.success:
            # Use result.download_url
    """

    # Default slide order for stitching
    DEFAULT_SLIDE_ORDER = [
        'streamlit_complete',
        'cultural_moments',
        'journey_environments',
        'catalyst_partners',
        'resonance_pathway',
        'consumer_journey',
    ]

    def __init__(
        self,
        api_base_url: str = API_BASE_URL,
        bucket: str = S3_BUCKET
    ):
        """
        Initialize the S3 export service.

        Args:
            api_base_url: Base URL for the API Gateway endpoints
            bucket: S3 bucket name for exports
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.bucket = bucket
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def generate_export_id(self) -> str:
        """Generate a unique export ID."""
        return str(uuid.uuid4())

    def get_presigned_upload_url(
        self,
        export_id: str,
        component_name: str
    ) -> Optional[str]:
        """
        Get a presigned URL for uploading a PPTX file to S3.

        Args:
            export_id: Unique identifier for this export session
            component_name: Name of the component (e.g., 'streamlit_complete')

        Returns:
            Presigned URL for PUT operation, or None if failed
        """
        try:
            response = self.session.post(
                f"{self.api_base_url}/presigned-url",
                json={
                    'action': 'upload',
                    'exportId': export_id,
                    'componentName': component_name,
                    'bucket': self.bucket
                },
                timeout=PRESIGNED_URL_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            url = data.get('url')

            if url:
                logger.info(f"Got presigned URL for {component_name}")
                return url
            else:
                logger.error(f"No URL in response: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get presigned URL: {e}")
            return None

    def upload_to_s3(
        self,
        presigned_url: str,
        pptx_bytes: bytes,
        content_type: str = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ) -> bool:
        """
        Upload PPTX bytes to S3 using a presigned URL.

        Args:
            presigned_url: Presigned PUT URL from get_presigned_upload_url
            pptx_bytes: Raw bytes of the PPTX file
            content_type: MIME type for the upload

        Returns:
            True if upload succeeded, False otherwise
        """
        try:
            # Use a separate session for S3 upload (different headers)
            response = requests.put(
                presigned_url,
                data=pptx_bytes,
                headers={
                    'Content-Type': content_type
                },
                timeout=UPLOAD_TIMEOUT
            )
            response.raise_for_status()

            logger.info(f"Successfully uploaded {len(pptx_bytes):,} bytes to S3")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

    def invoke_stitch(
        self,
        export_id: str,
        components: List[str],
        slide_order: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke the PPTX stitch Lambda to merge components.

        Args:
            export_id: Export session ID
            components: List of component names that were uploaded
            slide_order: Optional custom slide order

        Returns:
            Dict with 'downloadUrl', 's3Key', 'componentsIncluded' or None if failed
        """
        try:
            response = self.session.post(
                f"{self.api_base_url}/stitch",
                json={
                    'exportId': export_id,
                    'bucket': self.bucket,
                    'components': components,
                    'slideOrder': slide_order or self.DEFAULT_SLIDE_ORDER
                },
                timeout=STITCH_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()

            if 'downloadUrl' in data:
                logger.info(f"Stitch complete. Components: {data.get('componentsIncluded', [])}")
                return data
            else:
                logger.error(f"No downloadUrl in stitch response: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to invoke stitch: {e}")
            return None

    def export_and_stitch(
        self,
        session_state: Dict[str, Any],
        brand_name: str = "Brand",
        industry: str = "General",
        components: Optional[List[str]] = None,
        slide_order: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        export_id: Optional[str] = None
    ) -> ExportResult:
        """
        Complete export pipeline: generate PPTX, upload to S3, stitch, return URL.

        This is the main entry point for the export process.

        Args:
            session_state: Streamlit session state dictionary
            brand_name: Brand name for the presentation
            industry: Industry for the presentation
            components: List of components to include in stitch
            slide_order: Custom slide order for stitching
            progress_callback: Optional callback for progress updates (percent, message)
            export_id: Optional pre-generated export ID (useful when React components
                       have already uploaded with this ID)

        Returns:
            ExportResult with success status and download URL or error
        """
        def update_progress(percent: int, message: str):
            if progress_callback:
                progress_callback(min(percent, 100), message)

        # Use provided export_id or generate new one
        # Note: export_id should be set in st.session_state by results.py before calling this
        export_id = export_id or self.generate_export_id()
        logger.info(f"Starting export with ID: {export_id}")

        try:
            # Step 1: Generate PPTX
            update_progress(10, "Generating presentation...")
            logger.info("Generating PPTX...")

            from core.export_orchestrator import export_to_pptx
            pptx_bytes = export_to_pptx(
                session_state=session_state,
                brand_name=brand_name,
                industry=industry,
                progress_callback=lambda p, m: update_progress(10 + int(p * 0.3), m)
            )

            logger.info(f"Generated PPTX: {len(pptx_bytes):,} bytes")

            # Step 2: Get presigned upload URL
            update_progress(45, "Preparing upload...")
            logger.info("Getting presigned URL...")

            presigned_url = self.get_presigned_upload_url(export_id, 'streamlit_complete')
            if not presigned_url:
                return ExportResult(
                    success=False,
                    export_id=export_id,
                    error="Failed to get presigned upload URL"
                )

            # Step 3: Upload to S3
            update_progress(55, "Uploading to cloud...")
            logger.info("Uploading to S3...")

            if not self.upload_to_s3(presigned_url, pptx_bytes):
                return ExportResult(
                    success=False,
                    export_id=export_id,
                    error="Failed to upload PPTX to S3"
                )

            # Step 4: Invoke stitch Lambda
            update_progress(75, "Assembling final presentation...")
            logger.info("Invoking stitch Lambda...")

            # Include streamlit_complete plus any other specified components
            stitch_components = components or ['streamlit_complete']
            if 'streamlit_complete' not in stitch_components:
                stitch_components = ['streamlit_complete'] + stitch_components

            stitch_result = self.invoke_stitch(
                export_id=export_id,
                components=stitch_components,
                slide_order=slide_order
            )

            if not stitch_result:
                return ExportResult(
                    success=False,
                    export_id=export_id,
                    error="Failed to stitch presentation"
                )

            update_progress(100, "Export complete!")
            logger.info(f"Export complete. Download URL ready.")

            return ExportResult(
                success=True,
                export_id=export_id,
                download_url=stitch_result.get('downloadUrl'),
                s3_key=stitch_result.get('s3Key'),
                components_included=stitch_result.get('componentsIncluded', [])
            )

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return ExportResult(
                success=False,
                export_id=export_id,
                error=str(e)
            )

    def upload_component(
        self,
        export_id: str,
        component_name: str,
        pptx_bytes: bytes
    ) -> bool:
        """
        Upload a single component PPTX to S3.

        Useful for uploading React-generated components separately.

        Args:
            export_id: Export session ID (must match other components)
            component_name: Name of the component
            pptx_bytes: Raw PPTX bytes

        Returns:
            True if upload succeeded
        """
        presigned_url = self.get_presigned_upload_url(export_id, component_name)
        if not presigned_url:
            return False

        return self.upload_to_s3(presigned_url, pptx_bytes)

    def get_download_url(
        self,
        export_id: str,
        component_name: str = 'final'
    ) -> Optional[str]:
        """
        Get a presigned download URL for a component or final file.

        Args:
            export_id: Export session ID
            component_name: 'final' for stitched result, or component name

        Returns:
            Presigned download URL or None
        """
        try:
            response = self.session.post(
                f"{self.api_base_url}/presigned-url",
                json={
                    'action': 'download',
                    'exportId': export_id,
                    'componentName': component_name,
                    'bucket': self.bucket
                },
                timeout=PRESIGNED_URL_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            return data.get('url')

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get download URL: {e}")
            return None


# Convenience function for direct use
def export_to_s3_and_stitch(
    session_state: Dict[str, Any],
    brand_name: str = "Brand",
    industry: str = "General",
    components: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    export_id: Optional[str] = None
) -> ExportResult:
    """
    Convenience function for the complete export pipeline.

    Args:
        session_state: Streamlit session state
        brand_name: Brand name
        industry: Industry
        components: Components to include in stitch
        progress_callback: Progress callback (percent, message)
        export_id: Optional pre-generated export ID

    Returns:
        ExportResult with download URL or error
    """
    service = S3ExportService()
    return service.export_and_stitch(
        session_state=session_state,
        brand_name=brand_name,
        industry=industry,
        components=components,
        progress_callback=progress_callback,
        export_id=export_id
    )


# For testing
if __name__ == '__main__':
    # Test with mock data
    print("Testing S3 Export Service")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"S3 Bucket: {S3_BUCKET}")

    service = S3ExportService()
    export_id = service.generate_export_id()
    print(f"Generated export ID: {export_id}")

    # Test presigned URL generation
    url = service.get_presigned_upload_url(export_id, 'test_component')
    if url:
        print(f"Got presigned URL: {url[:100]}...")
    else:
        print("Failed to get presigned URL")
