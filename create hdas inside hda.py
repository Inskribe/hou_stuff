import hou  

node = hou.pwd()
geo = node.geometry()


# install hda
room_hdaPath = hou.hda.installFile('D:/Houdini Addons/my_assets/GT_wfc_rooms.hdalc')
room_hdaDef = hou.hda.definitionsInFile('D:/Houdini Addons/my_assets/GT_wfc_rooms.hdalc')
room_hda = room_hdaDef[0]
room_hda_ptg = room_hda.parmTemplateGroup()

# delcare global variables
head = hou.node('..')
link = hou.node('../link')
output = hou.node('../output')
g = head.type().definition().parmTemplateGroup()
parms_to_set = []
parms_to_ref = []


# remove old parameters and clear list
def clear_history():
    g.clear()
    head.type().definition().setParmTemplateGroup(g)
    head.type().definition().updateFromNode(head)
    parms_to_ref.clear()
    parms_to_set.clear()

# create and connect nodes
def create_node():
    copy = head.createNode('copytopoints', "copy_" + str(pt.number()))
    hda = head.createNode(room_hda.nodeType().name())
    copy.setFirstInput(hda)
    copy.setNextInput(link)
    return copy, hda,
   
# create merge node   
def merge_node():
    merge = head.createNode('merge')
    output.setFirstInput(merge)
    return merge

# create folder name    
def create_folder_name(ptnum, parms_from):
    l = str(len(geo.points())-1)
    n = (ptnum)
    if n == 0:
        folder_name = ('spawn_room')
    elif n == l:
        folder_name = ('boss_room')
    else:
        folder_name = ('room_' + str(ptnum))
    return folder_name

# create folder
def create_folder(name):
    folder = hou.FolderParmTemplate(name, name)
    folder.setFolderType(hou.folderType.Tabs)
    return folder

# determine template to create
def determine_template(parm_to_check):
    template_type = (parm_to_check.parmTemplate().type())
    return template_type


# create parm template base on hda templates
def create_parm(parm, ptnum):
    template = str(determine_template(parm))
    current_name = (str(parm.name() + str(ptnum)))
    path = parm.path()
    if template == 'parmTemplateType.Int':
        p = hou.IntParmTemplate(current_name, current_name, 1, default_value=(0,), default_expression=(path))
    elif template == 'parmTemplateType.String':
        p = hou.StringParmTemplate(current_name, current_name, 1, default_value=(), default_expression=(path))
    print(template)
    print(path)
    return p


# add created parm templates to folder
def transfer_parms(parms_from, ptnum):
    folder_name = create_folder_name(ptnum, parms_from)
    folder = create_folder(folder_name)
    for parm_from in parms_from:
        created_parm = create_parm(parm_from, ptnum)
        parms_to_ref.append(parm_from)       
        g.append(created_parm)
    head.setParmTemplateGroup(g) 

# get new parameters from head node
def get_head_parms():
    head_parms = head.parms()
    for parm in head_parms:
        parms_to_set.append(parm)

# set reference on head parms to control room hda parms
def set_parms():
    get_head_parms()
    for i in range(len(parms_to_set)):
        parm_to_set = parms_to_set[i]
        parm_to_ref = parms_to_ref[i]
        parm_to_set.set(parm_to_ref)
    

# update head definition
def update_hda():
    ptg = head.parmTemplateGroup()
    head.type().definition().setParmTemplateGroup(ptg)
    saveUnlockedNodes()

def saveUnlockedNodes():
    head.type().definition().updateFromNode(head)
    #head.matchCurrentDefinition()
    

clear_history()
merge = merge_node()

    
for pt in geo.points():
    copy, hda = create_node()
    merge.setNextInput(copy)
    copy.setParms({'targetgroup': ('@ptnum = ' + str(pt.number()))})
    parms_from = hda.parms()
    transfer_parms(parms_from, pt.number())
set_parms()
output.setDisplayFlag(True)    
update_hda()

print(parms_to_ref)
print(parms_to_set)