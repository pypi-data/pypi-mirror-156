import numpy as np
from ase.io import read
from shutil import copyfile
from elph.javerage import get_orbitals, catnip
from elph.phonons import write_phonons
from elph import chdir, mkdir
import json
import os

def load_phonons(pair_atoms, phonon_file='phonon.npz', 
                 map_file='atom_mapping.json'):
    """Loads phonon modes and returns frequencies, eigenvectors and number of q points

    Args:
        pair_atoms (list): Atomic indices of the interacting pair
        phonon_file (str, optional): Numpy file with the phonon modes. Defaults to 'phonon.npz'
        map_file (str, optional): JSON file generate to map atomic indices 
        of the wraped to the unwraped structure. Defaults to 'atom_mapping.json'

    Returns:
        tuple: vector of frequencies, vector of eigenvectors, and integer of the number of qpoints
    """
    # read phonon modes file
    phonon = np.load(phonon_file)

    # read mapping file
    with open(map_file, 'r') as json_file:
        mapping = list(map(int, json.load(json_file).keys()))
    
    # use mapping to order the wrapped phonon modes
    # based on the unwrapped atoms
    if len(mapping) > len(phonon['vecs'][0]):
        vecs_eav = np.tile(phonon['vecs'], [1, 2, 1])[:, mapping, :]
    else:
        vecs_eav = phonon['vecs'][:, mapping, :]

    # selecting only the phonon modes relevant to the 
    # interaction pair of molecules
    vecs_eav = vecs_eav[:, pair_atoms, :]

    return phonon['freqs'], vecs_eav, phonon['nq']

def get_displacements(atoms):
    """Returns displacement of each atom in each direction

    Args:
        atoms (Atoms): Atoms objects

    Yields:
        yield: (atom number, direction, sign)
    """
    latoms = len(atoms)
    for ia in range(latoms):
        for iv in range(3):
            for sign in [-1, 1]:
                yield (ia, iv, sign)

def displace_atom(atoms, ia, iv, sign, delta):
    """Displace one atomic position in the Atoms object

    Args:
        atoms (Atoms): Atoms object
        ia (int): atom index
        iv (int): direction index
        sign (str): sign of displacement in each direction
        delta (float): size of displacement

    Returns:
        Atoms: Updated Atoms object
    """
    new_atoms = atoms.copy()
    pos_av = new_atoms.get_positions()
    pos_av[ia, iv] += sign * delta
    new_atoms.set_positions(pos_av)
    return new_atoms

def finite_dif(delta=0.01):
    """Compute Gaussian calculation for displaced system

    Args:
        delta (float, optional): Size of displacement. Defaults to 0.01.
    """
    atoms = read('static.xyz')
    for ia, iv, sign in get_displacements(atoms):
        prefix = 'dj-{}-{}{}{}' .format(int(delta * 1000), 
                                        ia,
                                        'xyz'[iv],
                                        ' +-'[sign])
        new_structure = displace_atom(atoms, ia, iv, sign, delta)
        get_orbitals(new_structure, prefix)

def get_dj_matrix(jlists, delta):
    """Matrix containing gradient of J, the transfer integral

    Args:
        jlists (list): list of transfer integrals
        delta (float): size of displacement

    Returns:
        array: matrix containing gradient of j
    """
    latoms = len(jlists) // 6
    # array with j - delta (j minus)
    jm = np.empty([latoms, 3])
    jm[:, 0] = jlists[0::6]
    jm[:, 1] = jlists[2::6]
    jm[:, 2] = jlists[4::6]
    
    # array with j + delta (j plus)
    jp = np.empty([latoms, 3])
    jp[:, 0] = jlists[1::6]
    jp[:, 1] = jlists[3::6]
    jp[:, 2] = jlists[5::6]

    dj_matrix = (np.abs(jp) - np.abs(jm)) / (2 * delta)

    return dj_matrix

def get_deviation(pair_atoms, dj_av, temp):
    """Calculate standard deviation (sigma) of the transfer integral

    Args:
        pair_atoms (array): Numpy array of atomic indices of interacting pairs
        dj_av (array): Numpy array of gradient of J for all atoms in the pair for all directions
        temp (float): Temperature in eV

    Returns:
        float: standard deviation (sigma) of the transfer integral
    """
    freqs_e, vecs_eav, nq = load_phonons(pair_atoms)
    epcoup_e = np.einsum('av,eav->e', dj_av, vecs_eav)
    ssigma = (1 / nq) * np.sum(epcoup_e**2 / \
        (2 * np.tanh(freqs_e / (2 * temp))))

    return np.sqrt(ssigma)

def get_sigma(pair, delta=0.01, temp=0.025):
    """Calculate standard deviation of the transfer integral between a molecule pair using finite differences

    Args:
        pair (tuple): Pair name and molecules indices
        delta (float, optional): Size of displacement. Defaults to 0.01.
        temp (float, optional): Temperature in eV. Defaults to 0.025.

    Returns:
        float: standard deviation of the transfer integral in eV
    """
    mol1 = str(pair[1][0] + 1)
    mol2 = str(pair[1][1] + 1)
    molpair = str(pair[0])
    if not os.path.exists(molpair + '_disp_js.npz'):
        jlists = []
        # run Gaussian for displacements of first molecule
        with chdir(mol1):
            mkdir('displacements')
            with chdir('displacements'):
                copyfile('../' + mol1 + '.xyz', 'static.xyz')
                finite_dif(delta)

        # run Gaussian for displacements of second molecule
        with chdir(mol2):
            mkdir('displacements')
            with chdir('displacements'):
                copyfile('../' + mol2 + '.xyz', 'static.xyz')
                finite_dif(delta)

        # run Gaussian for displacements of the pair
        with chdir(molpair):
            mkdir('displacements')
            with chdir('displacements'):
                copyfile('../' + molpair + '.xyz', 'static.xyz')
                finite_dif(delta)

        # calculating j for each displacement of the first molecule
        path1 = mol1 + '/displacements/'
        path2 = mol2 + '/' + mol2
        path3 = molpair + '/displacements/'

        atoms = read(path1 + 'static.xyz')
        offset = len(atoms)
        for ia, iv, sign in get_displacements(atoms):
            prefix = 'dj-{}-{}{}{}' .format(int(delta * 1000), 
                                                ia,
                                                'xyz'[iv],
                                                ' +-'[sign])
            j = catnip(path1 + prefix, path2, path3 + prefix)
            jlists.append(j)

        # calculating j for each displacement of the second molecule
        path1 = mol1 + '/' + mol1
        path2 = mol2 + '/displacements/'
        path3 = molpair + '/displacements/'

        atoms = read(path2 + 'static.xyz')
        for ia, iv, sign in get_displacements(atoms):
            prefix_mol = 'dj-{}-{}{}{}' .format(int(delta * 1000), 
                                                    ia,
                                                    'xyz'[iv],
                                                    ' +-'[sign])
            prefix_pair = 'dj-{}-{}{}{}' .format(int(delta * 1000), 
                                                     ia + offset,
                                                    'xyz'[iv],
                                                    ' +-'[sign])
            j = catnip(path1, path2 + prefix_mol, path3 + prefix_pair)
            jlists.append(j)

        data = {'js': jlists}   
        np.savez_compressed(molpair + '_disp_js.npz', **data)

    else:
        jlists = np.load(molpair + '_disp_js.npz')['js']

    # Create GradJ matrix with a atoms and v directions
    dj_matrix_av = get_dj_matrix(jlists, delta)

    # Calculate sigma
    offset = len(dj_matrix_av) // 2
    pair_atoms = np.concatenate([np.arange((int(mol1) - 1) * offset, 
                                            int(mol1) * offset), 
                                 np.arange((int(mol2) - 1) * offset, 
                                            int(mol2) * offset)])

    sigma = get_deviation(pair_atoms, dj_matrix_av, temp)
    data = {molpair: sigma}
    
    print('Sigma_{} = {}' .format(pair[0], sigma))

    return sigma

def sigma():
    """Write phonon modes from phonopy result, 
    and calculate the standard deviation (sigma)
    for each pair of molecules. Write sigmas to JSON files
    """
    write_phonons()

    with open('all_pairs.json', 'r') as json_file:
        pairs = json.load(json_file)
    
    for pair in pairs.items():
        sigma = get_sigma(pair, delta=0.01)
        data = {pair[0]: sigma}
        with open('Sigma_' + pair[0] + '.json', 'w', encoding='utf-8') as f:
             json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    sigma()