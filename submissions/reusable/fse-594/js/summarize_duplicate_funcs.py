import json, os, sys, traceback, getopt




def measure(user_dir, task_id, start, end):
    global raw_data_dir, category2rank2target2infos

    current_pid = os.getpid()
    current_dir = os.getcwd()

    input_dir = current_dir
    files = os.listdir(input_dir)
    #files = [f for f in files if f.endswith('-category2target2type2script2infos.json')]
    #files = [f for f in files if f.endswith('-duplicate_cat2rank2target2infos.json')] # and not f.endswith('-used-category2type2target2infos.json')]
    f = user_dir + '-duplicate_cat2rank2target2infos.json'
    try:
        #rank = f.split('.')[0]
        input_file = os.path.join(input_dir, f)
        with open(input_file, 'r') as input_f:
            cat2rank2target2infos = json.loads(input_f.read())
            for category, rank2target2infos in cat2rank2target2infos.items():
                for rank, target2infos in rank2target2infos.items():
                    for target, infos in target2infos.items():
                        for info in infos:
                            if len(info) >= 15:
                                if info[5] == info[15]:
                                    continue
                                if info[-4].split('.')[1] != 'main':
                                    continue
                                if info[-4].split('.')[2] != '0':
                                    continue
                                if (info[9] == 'undefined' and info[3] != '(=)undefined') or (info[19] == 'undefined' and info[13] != '(=)undefined'):
                                    continue
                            else:
                                if info[0] == info[4]:
                                    continue
                                if info[3].split('.')[1] != 'main':
                                    continue
                                if info[3].split('.')[2].split('-')[0] != '0':
                                    continue
                                if info[7].split('.')[1] != 'main':
                                    continue
                                if info[7].split('.')[2].split('-')[0] != '0':
                                    continue
                                
                            if category not in category2rank2target2infos:
                                category2rank2target2infos[category] = dict()
                            if rank not in category2rank2target2infos[category]:
                                category2rank2target2infos[category][rank] = dict()
                            if target not in category2rank2target2infos[category][rank]:
                                category2rank2target2infos[category][rank][target] = list()

                            category2rank2target2infos[category][rank][target].append(info)

    except Exception as e:
        #print(e)
        pass







def main(argv):
    global raw_data_dir, num_instances, category2rank2target2infos

    parent_pid = os.getpid()
    try:
        opts, args = getopt.getopt(argv, 'hu:d:i:n:p:s:e:t:o:', ['help', 'user_dir=', 'exp_dir=', 'num=', 'process=', 'start=', 'end=', 'type=', 'output_dir='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

        
    user_dir = None
    num_instances = 512
    maximum_process_num = 8 # Change to 1 for debugging purpose
    start = 0
    end = None
    exp_dir = "exps"
    extract = False
    clean = False
    send = False
    #input_type = 'info2index2script'
    input_type = 'url2index'
    for opt, arg in opts:
        if opt in ('-u', '--user_dir'):
            user_dir = arg
        elif opt in ('-d', '--dir'):
            exp_dir = arg
        elif opt in ('-n', '--num'):
            num_instances = int(arg)
        elif opt in ('-p', '--process'):
            maximum_process_num = int(arg)
        elif opt in ('-s', '--start'):
            start = int(arg)
        elif opt in ('-e', '--end'):
            end = int(arg)
        elif opt in ('-t', '--type'):
            input_type = arg
        elif opt in ('-o', '--output_dir'):
            output_dir = arg
        elif opt in ('-h', '--help'):
            usage()
            sys.exit(0)


    category2rank2target2infos = dict()
    input_file = 'top-1m.csv'
    raw_data_dir = exp_dir

    try:
        os.chdir(exp_dir)
    except OSError as e:
        print(e)
        sys.exit(1)




    tasks = [i for i in range(num_instances-1, -1, -1)]
    for task in tasks:
        user_dir_group = '%s_%d' %(user_dir, task)
        try:
            measure(user_dir_group, task, start, end)
        except OSError as e:
            print(e)
            continue
    
    output_file = 'duplicate-category2rank2target2infos.json'
    output_file = os.path.join(output_dir, output_file)
    with open(output_file, 'w') as output_f:
        output_f.write(json.dumps(category2rank2target2infos))


    ranks = set()
    conflict_cnt = 0
    targets = set()
    for cat, rank2target2infos in category2rank2target2infos.items():
        print('\ntype: %s'%(cat))
        print('\t%d websites'%(len(rank2target2infos)))
        type_targets = set()
        type_conflict_cnt = 0
        for rank, target2infos in rank2target2infos.items():
            ranks.add(rank)
            for target, infos in target2infos.items():
                targets.add(target)
                conflict_cnt += len(infos)
                type_targets.add(target)
                type_conflict_cnt += len(infos)
        print('\t%d conflicts on %d targets'%(type_conflict_cnt, len(type_targets)))
    print('\nIn total %d duplicate function conflicts on %d functions, detected across %d websites'%(conflict_cnt, len(targets), len(ranks)))



if __name__ == '__main__':
    main(sys.argv[1:])
