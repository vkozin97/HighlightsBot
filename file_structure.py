import yadisk
import os.path as pth
import time
import pickle

token_file = pth.join('Data', 'yd_token.txt')
path_to_save_file_structure = pth.join('Data', 'file_structure.pkl')

def get_token(token_file=token_file):
    with open(token_file) as f:
        token = f.read()
    return token


root = "/Тренировки по средам"

y = yadisk.YaDisk(token=get_token())


def scan_path(path_after_root, publish_new=True, recursive=True, verbose=False):
    '''

    Parameters
    ----------
    path_after_root : str
        path to folder inside the root folder.
    publish_new : bool, optional
        Set to True if you want to publish all unpublished files and folders. The default is True.
    recursive : bool, optional
        Set to True if you want to reach the deepest files. The default is True.
    verbose : bool, optional
        Set to True to print out the information furing the scan. The default is True.

    Returns
    -------
    Dict with structure of the folder.

    '''
    
    path_after_root = path_after_root.lstrip('/')
    
    if verbose:
        print('Entering the folder', path_after_root)
    
    success = False
    while not success:
        try:
            resources = list(y.listdir(root + '/' + path_after_root))
            success = True
        except yadisk.exceptions.YaDiskError() as e:
            print('YDExeption occured for y.list_dir:\n' + e + '\n')
            time.sleep(2)
            
            
    folders = []
    files = []
    for r in resources:
        cur_dict = {'name': r.name, 'path': (path_after_root + '/' + r.name).lstrip('/')}
        if r.type == 'dir' and recursive:
            cur_dict['dir_content'] = scan_path(cur_dict['path'],
                                                publish_new=publish_new,
                                                recursive=recursive,
                                                verbose=verbose)
        if not r.public_url and publish_new:
            success = False
            if verbose:
                print('Publishing the', cur_dict['path'])
            while not success:
                try:
                    y.publish(r.path)
                    success = True
                except yadisk.exceptions.YaDiskError() as e:
                    print('YDException occured for y.publish:\n' + e + '\n')
                    time.sleep(60)
            success = False
            while not success:
                try:
                    r = y.get_meta(r.path)
                    success = True
                except yadisk.exceptions.YaDiskError() as e:
                    print('YDException occured for y.get_meta:\n' + e + '\n')
                    time.sleep(60)
            if verbose:
                print('Published the', cur_dict['path'])
        
        cur_dict['public_url'] = r.public_url
        
        if r.type == 'dir':
            folders.append(cur_dict)
        else:
            files.append(cur_dict)
        
        if verbose:
            print('Processed the', cur_dict['path'])
    
    if verbose:
        print('Exitting the folder', path_after_root)
    
    return {'folders': folders, 'files': files}


def save_structure(file_structure, file=path_to_save_file_structure):
    with open(file, 'wb') as f:
        pickle.dump(file_structure, f, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_structure(file=path_to_save_file_structure):
    with open(file, 'rb') as f:
        res = pickle.load(f)    
    return res

def update_file_structure():
    root_structure = scan_path('', publish_new=True, recursive=True, verbose=True)
    save_structure(root_structure)


if __name__ == '__main__':
    update_file_structure()