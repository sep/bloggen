from datetime import datetime
from pathlib import PurePath, Path
import os
from typing import Dict, List
import uuid

directive_symbol_start = '<!--$'
directive_symbol_end = '$-->'
timestamp_format = '%m-%d-%YT%H:%M:%S'
class Site_Info:

    def __init__(self, target_dir, user:str):
        self.target_dir = target_dir
        self.index = dict()
        self.relationships = dict()
        self.data = dict()
        self.user = user
        self.uuids = dict() # dict with keys: names values: uuids
        self.supported_directives = [{'name':'subjects', 'function': self.extract_subjects}, {'name':'tags', 'function': self.extract_tags}, {'name':'style', 'function': self.extract_style}]
        self.get_site_info()

    def generate_ids(self, paths: List, id_tag: str, username: str, return_mapping: bool=False) -> List[str]:
        ids_paths: List[Dict[str,str]] = [{ 'id': self.generate_id(username, id_tag), 'path': path } for path in paths]
        if return_mapping:
            return [ele['id'] for ele in ids_paths], ids_paths
        return [ele['id'] for ele in ids_paths]

    def get_site_info(self) -> dict():

        relationship_graph, data, index = self.build_site_info(self.target_dir)
        print(relationship_graph)
        # node_paths = self.__get_sub_directories(self.target_dir)
        # node_ids = self.generate_ids(node_paths, 'blog', self.user)
        
        # note_paths = self.__get_filepaths(self.target_dir)
        # note_ids, noteIds_notepaths = self.generate_ids(note_paths, 'note', self.user, True)
        
        # self.__create_index(self.target_dir, node_ids, note_ids)

        # # relationship object
        # # TODO
        # self.find_relationships()
        # # the first time ids are generates

        # # return a site_info dict
        # self.create_data(self.user, self.index, noteIds_notepaths)

    def __create_index(self, target_dir, node_ids, note_ids: List[str]):
        """
        index is a list of contents.
        index is not a record of relationships.
        """
        # root node is the highest dir
        rootNode = PurePath(target_dir).name

        # filepaths = self.__get_filepaths(target_dir)
        self.index.update({"rootNode":rootNode})
        self.index.update({"nodes":node_ids})
        self.index.update({"notes":note_ids})

    def find_relationships(self):
        """
        consider either bfs or dfs for this task
        use os.scandir() and __get_sub_directories() as an example
        """
        self.target_dir
        root = self.index['rootNode']
        # path of root?
        self.local_relationships(self.target_dir)

        

        # notes that are children of this blog

        pass

    def local_relationships(self,path):
        blogs = self.__get_sub_directories(path)
        # find local dirs
        # find local notes
        pass

    def create_data(self, user, index, noteIds_notepaths):
        """
        For all nodes, generate an id and a metadata field.
        For all notes, generate an entry as listed in the example.site.info.json
        """
        nodes = [{node: self.generate_id(user, "blog"), 'metadata': [self.node_metadata()]} for node in index['nodes']]
        notes = [self.create_note(noteId_notepath) for noteId_notepath in noteIds_notepaths]
        self.data['nodes'] = nodes
        self.data['notes'] = notes

    def create_note(self, noteId_notepath: Dict[str,str]):
        id = noteId_notepath['id']
        path = noteId_notepath['path']
        directive_data = self.extract_data(path)
        return {
            'id': id,
            'content': path,
            'subjects': directive_data['subjects'],
            'tags':directive_data['tags'],
            'metadata': self.note_metadata(path)
        }

    def create_note_new(self, id, path:Path):
        directive_data = self.extract_data(path.absolute())
        return {
            'id': id,
            'content': path,
            'subjects': directive_data['subjects'],
            'tags':directive_data['tags'],
            'metadata': self.note_metadata(path)
        }

    def node_metadata(self):
        """
        As you decide to add more metadata objects, return more objects from here
        """
        return {'timestamp': datetime.now().strftime(timestamp_format)}
    
    def note_metadata(self, path):
        """
        As you decide to add more metadata objects, return more objects from here
        """
        style = 'default' # TODO extract style from the file. It is a directive. use extract_style()
        return {'timestamp': datetime.now().strftime(timestamp_format),'style':style}

    def build_site_info(self, dir_name) -> list[str]:
        # figure out the root node.
        # root node will be missing from site_info json rn
        

        def recurse_dirs(relationship_graph, data, index, blog_id: str, dir: Path):
            print(f'called with blog_id {blog_id}')
            recursion_queue = []
            for f in dir.iterdir():
                if f.is_dir():
                    print(f.name)
                    child_blog_id = self.generate_id(self.user, "blog")
                    index['nodes'].append(child_blog_id)
                    data['nodes'].append(child_blog_id)
                    recursion_queue.append((child_blog_id,f))
                    print(f'for {f.name}, blog_id is {child_blog_id}')
                elif f.name.endswith('.md'):
                    print(f.name)
                    print(blog_id)
                    id = self.generate_id(self.user, "note")
                    path = f.absolute()
                    relationship_graph[blog_id]['notes'] = id
                    index['notes'].append(id)
                    data['notes'].append(self.create_note_new(id, path))

                    # ids_paths = [{ 'id': self.generate_id(self.user, "note"), 'path': f.absolute } for f in dir.iterdir()]
                    # ids_paths['id']
            for blog_id,dir in recursion_queue:
                relationship_graph, data, index = recurse_dirs(relationship_graph, data, index, blog_id, dir)

            return relationship_graph, data, index

        # for f in path.iterdir():
        #     if f.is_dir():
        #         # make id from p
        #         blog_id = self.generate_id(self.user, "blog")
        #         {blog_id: {
        #             'blogs': [],
        #             'notes': []
        #         }}
        #         # build relationship object

        #     # build child subdirs 
        path = Path(dir_name)
        root_id = 'the root node'
        return recurse_dirs({root_id: {'blogs': [], 'notes': []}}, {"nodes": [], "notes": []}, {"nodes": [],"notes": []}, root_id, path)

    def __get_sub_directories(self, dir_name) -> list[str]:
        sub_dirs = [f.name for f in os.scandir(dir_name) if f.is_dir()]
        return sub_dirs
    
    def __get_filepaths(self, dir_name) -> list[str]:
        sub_files = [f.path for f in os.scandir(dir_name) if f.is_file() and f.name.endswith('.md') ]
        return sub_files
    
    def __get_child_files(self, dir_name) -> list[str]:
        sub_files = [f.name for f in os.scandir(dir_name) if f.is_file() and f.name.endswith('.md') ]
        return sub_files
    
    def generate_id(self, user, prefix: str) -> str:
        return f'{prefix}_{user}_{uuid.uuid4().hex[:5]}'

    def extract_data(self, filepath: str, ):
        with open(filepath, 'r') as f:
            contents = f.read()
        directive_data: Dict[str: [str]] = self.get_directives(contents, filepath)
        return directive_data
        # TODO add support for directives that are commands
        # return self.execute_commands(directive_data)

    def get_directives(self, contents: str, filepath: str) -> Dict[str, List[str]]:
        """
        At present, directive commands do not have context. They are simply pieces of text that are ignored by html
        """
        supported_directives = [s['name'] for s in self.supported_directives]
        directives = {directive:set() for directive in supported_directives}
        substr_start = 0

        directive_index = contents.find(directive_symbol_start, substr_start)
        while directive_index != -1:    
            colon_index = contents.find(':', directive_index)
            directive_end_index = contents.find(directive_symbol_end, colon_index)
            directive_start = directive_index + len(directive_symbol_start)
            directive: str = contents[directive_start:colon_index].strip(' ').lower()
            directive_command: str = contents[colon_index+1:directive_end_index].strip(' ').split(',')

            if directive not in supported_directives:
                print(f'{directive} is not a supported directive. Found {directive} in {filepath}')
            else:
                for command in directive_command:
                    directives.setdefault(directive, set()).add(command)

            substr_start = directive_end_index
            directive_index = contents.find(directive_symbol_start, substr_start)

        return directives

    def execute_commands(self, found_directives: Dict[str, List[str]]):
        results = {}
        self.supported_directives
        for supported_directive in self.supported_directives: # [{'name':'subjects', 'function': self.extract_subjects}, {'name':'tags', 'function': self.extract_tags}]
            if supported_directive['name'] in found_directives:
                commands = found_directives[supported_directive['name']]
                for command in commands:
                    results[supported_directive['name']] = supported_directive['function'](command)
        return results

    def extract_tags(self, tag):
        return tag

    def extract_subjects(self,subject):
        return subject

    def extract_style(self, style):
        return style

    # def extract_data(self, nextraction_functions: Dict(str,List(Function))):
    #     # search for the symbol

    #     # goal: retrieve directives and their content

    #     #  return {{k, v(f)} for k,v in extraction_functions} # there is a method that yields the l and v of a single object here
    #     pass