import os
def makeFolder(filepath):
        directory=os.path.abspath(filepath)
        number=0
        for file_name in os.listdir(directory):
                print (file_name)                
                new_file_number = number + 1
 
                new_file_name = '%s/%s%d.%s' % (directory,'Img' , new_file_number,'nef')
                old_file_name = '%s/%s' % (directory, file_name)
 
                os.rename(old_file_name, new_file_name)
                number+=1
 
