# Reference: https://github.com/NVlabs/FourCastNet/blob/master/train.py, "restore_checkpoint" function
def load_model(model, model_path, device):
    model.zero_grad()
    if device=='cpu':
        checkpoint=torch.load(model_path, map_location=torch.device('cpu'))
    else:
        checkpoint=torch.load(model_path)
    try:
        new_state_dict=OrderedDict()
        for key, val in checkpoint['model_state'].items():
            name=key[7:]
            if name != 'ged':
                new_state_dict[name]=val
        model.load_state_dict(new_state_dict)
    except:
        model.load_state_dict(checkpoint['model_state'])
    model.eval()
    return model
