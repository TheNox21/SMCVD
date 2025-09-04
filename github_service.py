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
            self.github = Github()
    
    def validate_github_url(self, url):
        """Validate GitHub repository URL"""
        try:
            parsed = urlparse(url)
            if parsed.netloc != 'github.com':
                return False, "URL must be from github.com"
            
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                return False, "Invalid repository URL format"
            
            owner, repo = path_parts[0], path_parts[1]
            
            # Try to access the repository
            try:
                repo_obj = self.github.get_repo(f"{owner}/{repo}")
                return True, f"Repository {repo_obj.full_name} found"
            except Exception as e:
                return False, f"Repository not found or not accessible: {str(e)}"
                
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
    
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
        """Get repository information"""
        try:
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            owner, repo = path_parts[0], path_parts[1]
            
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            
            return {
                'name': repo_obj.name,
                'full_name': repo_obj.full_name,
                'description': repo_obj.description,
                'language': repo_obj.language,
                'stars': repo_obj.stargazers_count,
                'forks': repo_obj.forks_count,
                'updated_at': repo_obj.updated_at.isoformat() if repo_obj.updated_at else None,
                'default_branch': repo_obj.default_branch
            }
            
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")
    
    def find_solidity_files(self, github_url):
        """Find Solidity files in repository without cloning"""
        try:
            parsed = urlparse(github_url)
            path_parts = parsed.path.strip('/').split('/')
            owner, repo = path_parts[0], path_parts[1]
            
            repo_obj = self.github.get_repo(f"{owner}/{repo}")
            
            solidity_files = []
            
            def search_tree(tree, path=""):
                for item in tree.tree:
                    if item.type == "tree":
                        # Recursively search subdirectories
                        subtree = repo_obj.get_git_tree(item.sha)
                        search_tree(subtree, f"{path}/{item.path}" if path else item.path)
                    elif item.type == "blob" and item.path.endswith('.sol'):
                        solidity_files.append({
                            'path': f"{path}/{item.path}" if path else item.path,
                            'sha': item.sha,
                            'size': item.size
                        })
            
            # Start from root tree
            tree = repo_obj.get_git_tree(repo_obj.default_branch)
            search_tree(tree)
            
            return solidity_files
            
        except Exception as e:
            raise Exception(f"Failed to find Solidity files: {str(e)}")
    
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

