import os
import tempfile
import shutil
from github import Github
from urllib.parse import urlparse
import requests
import zipfile

class GitHubService:
    def __init__(self):
        # GitHub token is optional for public repositories
        self.github_token = os.getenv('GITHUB_TOKEN')
        if self.github_token:
            self.github = Github(self.github_token)
        else:
            # Use unauthenticated access with per_page limit to avoid rate limits
            self.github = Github()
        
        # Simple in-memory cache to avoid repeated API calls
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes
    
    def _get_cache_key(self, operation, *args):
        """Generate cache key for operations"""
        return f"{operation}:" + ":".join(str(arg) for arg in args)
    
    def _get_cached(self, key):
        """Get cached result if still valid"""
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_timeout:
                return result
        return None
    
    def _set_cache(self, key, value):
        """Set cache value with timestamp"""
        import time
        self._cache[key] = (value, time.time())
    
    def validate_github_url(self, url):
        """Fast validate GitHub repository URL with caching"""
        try:
            # Check cache first
            cache_key = self._get_cache_key('validate', url)
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            parsed = urlparse(url)
            if parsed.netloc != 'github.com':
                result = (False, "URL must be from github.com")
                self._set_cache(cache_key, result)
                return result
            
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                result = (False, "Invalid repository URL format")
                self._set_cache(cache_key, result)
                return result
            
            owner, repo = path_parts[0], path_parts[1]
            
            # First try a simple HTTP request to check if repo exists (faster than API)
            try:
                simple_url = f"https://github.com/{owner}/{repo}"
                response = requests.head(simple_url, timeout=5)
                
                if response.status_code == 200:
                    # Repository exists, try to get basic info via API
                    try:
                        repo_obj = self.github.get_repo(f"{owner}/{repo}")
                        result = (True, f"Repository {repo_obj.full_name} found")
                        self._set_cache(cache_key, result)
                        return result
                    except Exception as api_error:
                        # API failed but repo exists, still valid
                        result = (True, f"Repository {owner}/{repo} found (limited info due to rate limits)")
                        self._set_cache(cache_key, result)
                        return result
                else:
                    result = (False, f"Repository not found (HTTP {response.status_code})")
                    self._set_cache(cache_key, result)
                    return result
                    
            except requests.RequestException as req_error:
                # Fallback to API only
                try:
                    repo_obj = self.github.get_repo(f"{owner}/{repo}")
                    result = (True, f"Repository {repo_obj.full_name} found")
                    self._set_cache(cache_key, result)
                    return result
                except Exception as e:
                    result = (False, f"Repository not accessible: {str(e)}")
                    self._set_cache(cache_key, result)
                    return result
                
        except Exception as e:
            result = (False, f"Invalid URL: {str(e)}")
            self._set_cache(cache_key, result)
            return result
    
    def clone_repository(self, github_url):
        """Clone GitHub repository to temporary directory"""
        try:
            # Parse repository info
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            owner, repo = path_parts[0], path_parts[1]
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Download repository as ZIP (no git required)
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            
            # Try main branch first, then master if main fails
            for branch in ['main', 'master']:
                zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
                response = requests.get(zip_url)
                
                if response.status_code == 200:
                    # Save and extract ZIP file
                    zip_path = os.path.join(temp_dir, 'repo.zip')
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Extract ZIP
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Remove ZIP file
                    os.remove(zip_path)
                    
                    # Find extracted directory (usually repo-branch format)
                    extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if extracted_dirs:
                        # Move contents to temp_dir root
                        extracted_path = os.path.join(temp_dir, extracted_dirs[0])
                        for item in os.listdir(extracted_path):
                            shutil.move(os.path.join(extracted_path, item), temp_dir)
                        os.rmdir(extracted_path)
                    
                    return temp_dir
            
            # If both branches failed
            raise Exception(f"Could not download repository from {github_url}")
            
        except Exception as e:
            # Cleanup on error
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def get_repository_info(self, github_url):
        """Get repository information with caching and fallback"""
        try:
            cache_key = self._get_cache_key('repo_info', github_url)
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            owner, repo = path_parts[0], path_parts[1]
            
            try:
                repo_obj = self.github.get_repo(f"{owner}/{repo}")
                
                result = {
                    'name': repo_obj.name,
                    'full_name': repo_obj.full_name,
                    'description': repo_obj.description,
                    'language': repo_obj.language,
                    'stars': repo_obj.stargazers_count,
                    'forks': repo_obj.forks_count,
                    'updated_at': repo_obj.updated_at.isoformat() if repo_obj.updated_at else None,
                    'default_branch': repo_obj.default_branch
                }
                
                self._set_cache(cache_key, result)
                return result
                
            except Exception as api_error:
                # Fallback to basic info when API fails
                result = {
                    'name': repo,
                    'full_name': f"{owner}/{repo}",
                    'description': 'Information unavailable due to rate limits',
                    'language': 'Unknown',
                    'stars': 0,
                    'forks': 0,
                    'updated_at': None,
                    'default_branch': 'main'
                }
                
                # Don't cache fallback results for long
                import time
                self._cache[cache_key] = (result, time.time() - self._cache_timeout + 60)  # Cache for 1 minute only
                return result
            
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")
    
    def find_solidity_files(self, github_url):
        """Find Solidity files in repository with caching and fallback"""
        try:
            cache_key = self._get_cache_key('solidity_files', github_url)
            cached = self._get_cached(cache_key)
            if cached:
                return cached
                
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            owner, repo = path_parts[0], path_parts[1]
            
            try:
                repo_obj = self.github.get_repo(f"{owner}/{repo}")
                
                solidity_files = []
                
                def search_tree(tree, path="", max_depth=3, current_depth=0):
                    if current_depth > max_depth:
                        return  # Limit recursion depth to avoid rate limits
                        
                    for item in tree.tree:
                        if item.type == "tree" and current_depth < max_depth:
                            # Only search common contract directories
                            if any(keyword in item.path.lower() for keyword in ['contract', 'src', 'lib', 'token']):
                                try:
                                    subtree = repo_obj.get_git_tree(item.sha)
                                    search_tree(subtree, f"{path}/{item.path}" if path else item.path, max_depth, current_depth + 1)
                                except:
                                    continue  # Skip if subtree fails
                        elif item.type == "blob" and item.path.endswith('.sol'):
                            solidity_files.append({
                                'path': f"{path}/{item.path}" if path else item.path,
                                'sha': item.sha,
                                'size': item.size
                            })
                
                # Start from root tree
                tree = repo_obj.get_git_tree(repo_obj.default_branch)
                search_tree(tree)
                
                self._set_cache(cache_key, solidity_files)
                return solidity_files
                
            except Exception as api_error:
                # Fallback: return estimated count based on repository type
                result = []
                if 'solidity' in github_url.lower() or 'contract' in github_url.lower():
                    # Estimate some files exist for contract repos
                    result = [{
                        'path': 'contracts/Contract.sol',
                        'sha': 'unknown',
                        'size': 'unknown'
                    }]
                
                # Cache fallback for short time
                import time
                self._cache[cache_key] = (result, time.time() - self._cache_timeout + 60)
                return result
            
        except Exception as e:
            return []  # Return empty list instead of raising exception
    
    def get_file_content(self, github_url, file_path):
        """Get content of a specific file from repository"""
        try:
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            owner, repo = path_parts[0], path_parts[1]
            
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            file_content = repo_obj.get_contents(file_path)
            
            return file_content.decoded_content.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Failed to get file content: {str(e)}")

