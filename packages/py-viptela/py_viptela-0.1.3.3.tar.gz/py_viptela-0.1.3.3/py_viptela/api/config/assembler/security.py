from py_viptela.query_builder import Builder
from py_viptela import HttpMethods

class SecurityAssembly(object):
    """
    Configuration - Policy Security Assembler API
    
    Implements GET POST DEL PUT methods for Policy Security Assembler endpoints

    """

    def __init__(self, session, host, port):
        self.host = host
        self.port = port
        self.client = HttpMethods.HttpClient(session=session)
    
    
    def preview(self, policyassembly):
        """
        Get policy assembly preview
        
        Parameters:
        policyassembly:	Policy assembly
        
        Returns
        response    (dict)
        
        
        """
        
        endpoint = f"https://{self.host}:{self.port}/dataservice/template/policy/assembly/security"
        response = self.client.apiCall(HttpMethods.POST, endpoint, policyassembly)
        return response


    def previewById(self, id):
        """
        Get policy assembly preview
        
        Parameters:
        id	 (string):	Policy Id
        
        Returns
        response    (dict)
        
        
        """
        
        endpoint = f"https://{self.host}:{self.port}/dataservice/template/policy/assembly/security/{id}"
        response = self.client.apiCall(HttpMethods.GET, endpoint)
        return response


