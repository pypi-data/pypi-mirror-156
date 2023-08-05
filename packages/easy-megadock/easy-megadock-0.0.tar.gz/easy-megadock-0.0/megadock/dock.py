import os
from tqdm import trange


class Docktools(object):
    def __init__(self, receptor, ligand, output_folder="", weight=1):
        self.__megadock_gpu = os.path.dirname(__file__) + '/../tools/megadock-gpu'
        self.__decoygen = os.path.dirname(__file__) + '/../tools/decoygen'
        self.__receptor = receptor
        self.__ligand = ligand
        self.weight = weight
        self.output_folder = output_folder
        if not os.path.exists('.megadock'):
            os.makedirs('.megadock')
        self.tmpfolder = os.path.join('.megadock', str(os.getpid()))
        self.tmp_output_file = os.path.join(self.tmpfolder, 'tmp.out')
        self.flag = False
    
    def docking(self, info=True):
        print('receptor: {}, ligand: {}, docking...'.format(self.__receptor, self.__ligand))

        
        if not os.path.exists(self.tmpfolder):
            os.makedirs(self.tmpfolder)
        
        cmd = self.__megadock_gpu + ' -R {} -L {} -o {} -W {}'.format(
            self.__receptor, 
            self.__ligand, 
            self.tmp_output_file,
            self.weight)

        if not info:
            tmp_tail = ' > ' + os.path.join(self.tmpfolder, 'docking.log')
            cmd += tmp_tail
        os.system(cmd)
        self.flag = True
        
        print('receptor: {}, ligand: {}, docking done!'.format(self.__receptor, self.__ligand))
        
    def getres(self, topk=100):
        print('receptor: {}, ligand: {}, generating results...'.format(self.__receptor, self.__ligand))
        
        if not self.flag:
            self.docking()
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        cmd = self.__decoygen + ' {} {} {} {}'
        for idx in trange(1, topk + 1):
            # print(str(idx))
            target_ligand = 'r_ligand_' + str(idx) + '.pdb'
            # target_ligand = 'r_ligand_' + str(idx) + '.pdb'
            target_ligand = os.path.join(self.output_folder, target_ligand)
            # print(target_ligand)
            tmp_cmd = cmd.format(target_ligand, self.__ligand, self.tmp_output_file, idx)
            # print(tmp_cmd)
            os.system(tmp_cmd)
            
        print('receptor: {}, ligand: {}, generating results done!'.format(self.__receptor, self.__ligand))
        
    def __del__(self):
        os.system('rm -rf ' + self.tmpfolder)