from data import Event, Paper
from pathlib import Path
import pypandoc
import shutil
import jupytext

root: Path = Path('crress/works')

latex_ignore = [
    '.fdb_latexmk',
    '.gz',
    '.pdf',
    '.fls',
    '.log',
    '.aux'
]

main_file_dict = {
    
}

def get_events():
    
    event_list = []
    
    for directory in root.glob("[!.]*"): # Don't include hidden files
        papers = []
        for paper_folder in directory.glob("[!.][!converted]*"):
            
            # try the dict first
            main_file = main_file_dict.get(directory.name)
            if main_file is not None:
                main_file = main_file_dict.get(directory.name).get(paper_folder.name)

            if main_file is None:
                non_dir = [x for x in paper_folder.glob("[!.]*") if not x.is_dir() and not x.suffix in latex_ignore]
                if len(non_dir) == 1:
                    print(f"assuming that main file for {paper_folder} in {directory} is {non_dir[0].name}")
                    main_file = non_dir[0]
                else:
                    raise Exception("Can't find main file")
                
            papers.append(
                Paper(
                    name=paper_folder.name,
                    path=paper_folder,
                    converted_path=paper_folder.parents[0] / 'converted' / paper_folder.name,
                    main_file=main_file,
                )
            )
            
        event_list.append(Event(
            name=directory.name,
            papers = papers,
            path = directory
        ))
    return event_list

def pandoc_convert(paper: Paper, fmt : str=None):
    if fmt is None:
        fmt=paper.extension()
    new_main_file_path = paper.converted_path / paper.main_file.name
    return pypandoc.convert_file(str(new_main_file_path), 
                                 'markdown+yaml_metadata_block', 
                                 outputfile=str(new_main_file_path.with_suffix('.qmd'))
                                 )
    
def jupytext_convert(paper: Paper, fmt: str=None):
    if fmt is None:
        fmt = paper.extension()
    new_main_file_path = paper.converted_path / paper.main_file.name
    
    notebook = jupytext.read(str(new_main_file_path))
    
    return jupytext.write(notebook, str(new_main_file_path.with_suffix('.qmd')), fmt='qmd')
                          
class PandocConverter:
    pass

class JupytextConverter:
    pass
    

if __name__ == '__main__':

    events = get_events()
    
    for event in events:
        for paper in event.papers:
            if paper.extension().lower() in ['qmd', 'rmd']:
                shutil.copytree(paper.path, paper.converted_path, dirs_exist_ok=True)
                continue
            elif paper.extension().lower() in ['ipynb'] :
                shutil.copytree(paper.path, paper.converted_path, dirs_exist_ok=True)
                jupytext_convert(paper, fmt='qmd')
            else:
                shutil.copytree(paper.path, paper.converted_path, dirs_exist_ok=True)
                pandoc_convert(paper, fmt='markdown+yaml_metadata_block')

    
