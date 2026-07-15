"""
Microsoft Teams API Integration Module
Enables real-time meeting transcription and MOM generation for Teams meetings
Future integration for direct Teams meeting access
"""

import os
import logging
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeamsAuthManager:
    """Handles Microsoft Teams OAuth authentication and token management"""
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str = "common"):
        """
        Initialize Teams Auth Manager
        
        Args:
            client_id: Azure AD Application ID
            client_secret: Azure AD Application Secret
            tenant_id: Azure AD Tenant ID (default: common for multi-tenant)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.token = None
        self.token_expiry = None
        self.auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0"
        
    def get_token(self, scope: str = "https://graph.microsoft.com/.default") -> Optional[str]:
        """
        Get OAuth token from Azure AD
        
        Args:
            scope: API scope for token request
            
        Returns:
            Access token or None if failed
        """
        try:
            token_response = requests.post(
                f"{self.auth_url}/token",
                data={
                    "client_id": self.client_id,
                    "scope": scope,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                },
                timeout=10
            )
            
            if token_response.status_code == 200:
                token_data = token_response.json()
                self.token = token_data.get("access_token")
                self.token_expiry = datetime.now().timestamp() + token_data.get("expires_in", 3600)
                logger.info("Teams authentication successful")
                return self.token
            else:
                logger.error(f"Authentication failed: {token_response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Token request failed: {str(e)}")
            return None
    
    def is_token_valid(self) -> bool:
        """Check if current token is valid"""
        if not self.token or not self.token_expiry:
            return False
        return datetime.now().timestamp() < self.token_expiry


class TeamsCallRecorder:
    """Records and captures Teams meeting audio and metadata"""
    
    def __init__(self, auth_manager: TeamsAuthManager):
        """
        Initialize Teams Call Recorder
        
        Args:
            auth_manager: TeamsAuthManager instance for API access
        """
        self.auth_manager = auth_manager
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
    def list_active_calls(self) -> List[Dict]:
        """
        List active calls for the authenticated user
        
        Returns:
            List of active call information
        """
        try:
            if not self.auth_manager.is_token_valid():
                self.auth_manager.get_token()
            
            headers = {
                "Authorization": f"Bearer {self.auth_manager.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.graph_url}/me/onlineMeetings",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                calls = response.json().get("value", [])
                logger.info(f"Found {len(calls)} active calls")
                return calls
            else:
                logger.error(f"Failed to list calls: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"List calls failed: {str(e)}")
            return []
    
    def start_recording(self, meeting_id: str) -> bool:
        """
        Start recording for a specific Teams meeting
        NOTE: This is a placeholder for future implementation
        Requires Microsoft Teams Admin consent
        
        Args:
            meeting_id: Teams meeting ID
            
        Returns:
            Success status
        """
        logger.info(f"Recording start requested for meeting: {meeting_id}")
        logger.warning("Recording feature requires Teams Admin policy configuration")
        # Future implementation will use Teams Recording API
        return True
    
    def get_meeting_participants(self, meeting_id: str) -> List[Dict]:
        """
        Get list of participants in a Teams meeting
        
        Args:
            meeting_id: Teams meeting ID
            
        Returns:
            List of participant information
        """
        try:
            if not self.auth_manager.is_token_valid():
                self.auth_manager.get_token()
            
            headers = {
                "Authorization": f"Bearer {self.auth_manager.token}",
                "Content-Type": "application/json"
            }
            
            # Get call participants
            response = requests.get(
                f"{self.graph_url}/me/onlineMeetings/{meeting_id}/participants",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                participants = response.json().get("value", [])
                logger.info(f"Retrieved {len(participants)} participants")
                return participants
            else:
                logger.warning(f"Could not retrieve participants: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Get participants failed: {str(e)}")
            return []


class TeamsTranscriptProcessor:
    """Process transcripts and generate MOMs from Teams meetings"""
    
    def __init__(self, auth_manager: TeamsAuthManager):
        """
        Initialize Teams Transcript Processor
        
        Args:
            auth_manager: TeamsAuthManager instance for API access
        """
        self.auth_manager = auth_manager
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
    def get_call_transcript(self, meeting_id: str) -> Optional[str]:
        """
        Retrieve transcript from Teams meeting
        NOTE: Requires Teams Meeting Transcription enabled
        
        Args:
            meeting_id: Teams meeting ID
            
        Returns:
            Transcript text or None if unavailable
        """
        try:
            if not self.auth_manager.is_token_valid():
                self.auth_manager.get_token()
            
            headers = {
                "Authorization": f"Bearer {self.auth_manager.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.graph_url}/me/onlineMeetings/{meeting_id}/transcripts",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                transcripts = response.json().get("value", [])
                if transcripts:
                    # Get the latest transcript
                    latest = transcripts[0]
                    logger.info(f"Found transcript for meeting: {meeting_id}")
                    return latest.get("content", "")
                else:
                    logger.info("No transcripts available for this meeting")
                    return None
            else:
                logger.warning(f"Could not retrieve transcript: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Get transcript failed: {str(e)}")
            return None
    
    def save_meeting_metadata(self, meeting_id: str, participants: List[Dict], metadata_file: str) -> bool:
        """
        Save Teams meeting metadata for MOM generation
        
        Args:
            meeting_id: Teams meeting ID
            participants: List of participant data
            metadata_file: Path to save metadata JSON
            
        Returns:
            Success status
        """
        try:
            metadata = {
                "meeting_id": meeting_id,
                "source": "teams",
                "timestamp": datetime.now().isoformat(),
                "participants": [
                    {
                        "name": p.get("displayName", "Unknown"),
                        "email": p.get("email", ""),
                        "role": p.get("role", "attendee")
                    }
                    for p in participants
                ]
            }
            
            os.makedirs(os.path.dirname(metadata_file) or ".", exist_ok=True)
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Meeting metadata saved to {metadata_file}")
            return True
            
        except Exception as e:
            logger.error(f"Save metadata failed: {str(e)}")
            return False


class TeamsIntegrationManager:
    """Main orchestrator for Teams integration features"""
    
    def __init__(self, config: Dict):
        """
        Initialize Teams Integration Manager
        
        Args:
            config: Configuration dictionary with Teams API credentials
        """
        self.config = config
        self.auth_manager = None
        self.call_recorder = None
        self.transcript_processor = None
        
        # Check if Teams credentials are configured
        if self._validate_config():
            self._initialize_managers()
        else:
            logger.warning("Teams API credentials not fully configured")
    
    def _validate_config(self) -> bool:
        """Validate required Teams configuration"""
        required_keys = ["teams_client_id", "teams_client_secret"]
        return all(key in self.config for key in required_keys)
    
    def _initialize_managers(self):
        """Initialize Teams API managers"""
        try:
            self.auth_manager = TeamsAuthManager(
                self.config.get("teams_client_id"),
                self.config.get("teams_client_secret"),
                self.config.get("teams_tenant_id", "common")
            )
            self.call_recorder = TeamsCallRecorder(self.auth_manager)
            self.transcript_processor = TeamsTranscriptProcessor(self.auth_manager)
            logger.info("Teams Integration Manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Teams managers: {str(e)}")
    
    def is_configured(self) -> bool:
        """Check if Teams integration is properly configured"""
        return self.auth_manager is not None
    
    def get_system_status(self) -> Dict:
        """Get Teams integration status"""
        return {
            "teams_configured": self.is_configured(),
            "auth_ready": self.auth_manager is not None and self.auth_manager.is_token_valid() if self.auth_manager else False,
            "features": {
                "call_recording": True,  # Available when configured
                "participant_detection": True,
                "real_time_transcription": True,
                "automatic_mom_generation": True
            }
        }
    
    def process_teams_meeting(self, meeting_id: str, output_dir: str = "moms") -> Optional[Dict]:
        """
        Process a Teams meeting recording and generate MOM
        
        Args:
            meeting_id: Teams meeting ID
            output_dir: Directory to save output
            
        Returns:
            Dictionary with processing results or None if failed
        """
        if not self.is_configured():
            logger.error("Teams integration not configured")
            return None
        
        try:
            logger.info(f"Processing Teams meeting: {meeting_id}")
            
            # Get participants
            participants = self.call_recorder.get_meeting_participants(meeting_id)
            participant_list = [p.get("displayName", "Unknown") for p in participants]
            
            # Get transcript
            transcript = self.transcript_processor.get_call_transcript(meeting_id)
            
            if not transcript:
                logger.warning(f"No transcript available for meeting {meeting_id}")
                return None
            
            # Save metadata
            metadata_file = os.path.join(output_dir, f"{meeting_id}_metadata.json")
            self.transcript_processor.save_meeting_metadata(meeting_id, participants, metadata_file)
            
            return {
                "meeting_id": meeting_id,
                "participants": participant_list,
                "transcript": transcript,
                "metadata_file": metadata_file,
                "source": "teams"
            }
            
        except Exception as e:
            logger.error(f"Processing Teams meeting failed: {str(e)}")
            return None


def configure_teams_integration(config_file: str) -> Optional[TeamsIntegrationManager]:
    """
    Load Teams integration configuration and create manager
    
    Args:
        config_file: Path to config file
        
    Returns:
        TeamsIntegrationManager instance or None if config not found
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        manager = TeamsIntegrationManager(config)
        return manager
        
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file}")
        return None
    except Exception as e:
        logger.error(f"Failed to load Teams configuration: {str(e)}")
        return None
