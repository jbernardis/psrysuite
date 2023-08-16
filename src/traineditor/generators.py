def GenerateAR(tr, blks):		
	trainid = tr.GetTrainID()
	lastBlock = tr.GetStartBlock()
	blkSeq = tr.GetSteps()
	script = {}
	for b in blkSeq:
		if len(script) == 0:
			script["origin"] = lastBlock
			
		if blks is None or b["block"] in blks:
			trigger = 'F' if b["trigger"] == "Front" else 'R'			
			script[lastBlock] = {"route": b["route"], "trigger": trigger}
		lastBlock = b["block"]
		
	script["terminus"] = lastBlock

	return trainid, script
