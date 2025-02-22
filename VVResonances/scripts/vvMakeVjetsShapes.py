#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.plotting.StackPlotter import StackPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

parser = optparse.OptionParser()
parser.add_option("-s","--sample",dest="sample",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for shape",default='')
parser.add_option("-o","--output",dest="output",help="Output JSON",default='')
parser.add_option("-m","--min",dest="mini",type=float,help="min MJJ",default=40)
parser.add_option("-M","--max",dest="maxi",type=float,help="max MJJ",default=160)
parser.add_option("--store",dest="store",type=str,help="store fitted parameters in this file",default="")
parser.add_option("--corrFactorW",dest="corrFactorW",type=float,help="add correction factor xsec",default=0.205066345)
parser.add_option("--corrFactorZ",dest="corrFactorZ",type=float,help="add correction factor xsec",default=0.09811023622)
parser.add_option("-f","--fix",dest="fixPars",help="Fixed parameters",default="1")
parser.add_option("--minMVV","--minMVV",dest="minMVV",type=float,help="mVV variable",default=1)
parser.add_option("--maxMVV","--maxMVV",dest="maxMVV",type=float, help="mVV variable",default=1)
parser.add_option("--binsMVV",dest="binsMVV",help="use special binning",default="")
parser.add_option("-t","--triggerweight",dest="triggerW",action="store_true",help="Use trigger weights",default=False)


(options,args) = parser.parse_args()

samples={}
lumi = args[1]
print "luminosity is "+str(lumi)

def getBinning(binsMVV,minx,maxx,bins):
    l=[]
    if binsMVV=="":
        for i in range(0,bins+1):
            l.append(minx + i* (maxx - minx)/bins)
    else:
        s = binsMVV.split(",")
        for w in s:
            l.append(int(w))
    return l

def returnString(func,ftype,varname):
    if ftype.find("pol")!=-1:
        st='0'
        for i in range(0,func.GetNpar()):
            st=st+"+("+str(func.GetParameter(i))+")"+("*{varname}".format(varname=varname)*i)
        return st    
    else:
        return ""



def doFit(fitter,histo,histo_nonRes,label,leg=''):
  params={}
  print "fitting "+histo.GetName()+" contribution "    
  exp  = ROOT.TF1("gaus" ,"gaus",55,215)  
  histo_nonRes.Fit(exp,"R")
 
  gauss  = ROOT.TF1("gauss" ,"gaus",74,94) 
  if histo.GetName().find("Z")!=-1:
      gauss = ROOT.TF1("gauss","gaus",80,100)
  histo.Fit(gauss,"R")
  mean = gauss.GetParameter(1)
  sigma = gauss.GetParameter(2)
 
  print "____________________________________"
  print "mean "+str(mean)
  print "sigma "+str(sigma)
  print "set paramters of double CB constant aground the ones from gaussian fit"
  fitter.w.var("mean").setVal(mean)
  fitter.w.var("mean").setConstant(1)
  #fitter.w.var("sigma").setVal(sigma)
  #fitter.w.var("sigma").setConstant(1)
  print "_____________________________________"
  fitter.importBinnedData(histo,['x'],'data')
  fitter.fit('model','data',[ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Save(1),ROOT.RooFit.Range(55,120)]) #55,140 works well with fitting only the resonant part
 #ROOT.RooFit.Minos(ROOT.kTRUE)
  fitter.projection("model","data","x","debugJ"+leg+"_"+label+"_Res.pdf",0,False,"m_{jet}")
  
  
  c= getCanvas(label)
  histo_nonRes.SetMarkerStyle(1)
  histo_nonRes.SetMarkerColor(ROOT.kBlack)
  histo_nonRes.GetXaxis().SetTitle("m_{jet}")
  histo_nonRes.GetYaxis().SetTitleOffset(1.5)
  histo_nonRes.GetYaxis().SetTitle("events")
  histo_nonRes.Draw("p")
  exp.SetLineColor(ROOT.kRed)
  exp.Draw("same")
  text = ROOT.TLatex()
  text.DrawLatexNDC(0.13,0.92,"#font[62]{CMS} #font[52]{Simulation}")
  c.SaveAs("debugJ"+leg+"_"+label+"_nonRes.pdf")
  
  
  
  if leg!='':
   params[label+"_Res_"+leg]={"mean": {"val": fitter.w.var("mean").getVal(), "err": fitter.w.var("mean").getError()}, "sigma": {"val": fitter.w.var("sigma").getVal(), "err": fitter.w.var("sigma").getError()}, "alpha":{ "val": fitter.w.var("alpha").getVal(), "err": fitter.w.var("alpha").getError()},"alpha2":{"val": fitter.w.var("alpha2").getVal(),"err": fitter.w.var("alpha2").getError()},"n":{ "val": fitter.w.var("n").getVal(), "err": fitter.w.var("n").getError()},"n2": {"val": fitter.w.var("n2").getVal(), "err": fitter.w.var("n2").getError()}}
   params[label+"_nonRes_"+leg]={"mean": {"val":exp.GetParameter(1),"err":exp.GetParError(1)},"sigma": {"val":exp.GetParameter(2),"err":exp.GetParError(2)}}
  else:
   params[label+"_Res"]={"mean": {"val": fitter.w.var("mean").getVal(), "err": fitter.w.var("mean").getError()}, "sigma": {"val": fitter.w.var("sigma").getVal(), "err": fitter.w.var("sigma").getError()}, "alpha":{ "val": fitter.w.var("alpha").getVal(), "err": fitter.w.var("alpha").getError()},"alpha2":{"val": fitter.w.var("alpha2").getVal(),"err": fitter.w.var("alpha2").getError()},"n":{ "val": fitter.w.var("n").getVal(), "err": fitter.w.var("n").getError()},"n2": {"val": fitter.w.var("n2").getVal(), "err": fitter.w.var("n2").getError()}}
   params[label+"_nonRes"]={"mean": {"val":exp.GetParameter(1),"err":exp.GetParError(1)},"sigma": {"val":exp.GetParameter(2),"err":exp.GetParError(2)}}
  return params


def getCanvas(name):
    c=ROOT.TCanvas(name,name)       
    c.cd() 
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetLeftMargin(0.13)
    c.SetRightMargin(0.08)
    c.SetTopMargin( 0.1 )
    c.SetBottomMargin( 0.12 )
    return c

########################################3

label = options.output.split(".root")[0]
t  = label.split("_")
el=""
for words in t:
    if words.find("HP")!=-1 or words.find("LP")!=-1:
        continue
    el+=words+"_"
label = el

samplenames = options.sample.split(",")
for filename in os.listdir(args[0]):
    if filename.find(".")==-1:
        print "in "+str(filename)+"the separator . was not found. -> continue!"
        continue
    for samplename in samplenames:
        if not (filename.find(samplename)!=-1):
            continue


        fnameParts=filename.split('.')
        print "fnameParts "+str(fnameParts)
        fname=fnameParts[0]
        ext=fnameParts[1]
        if ext.find("root") ==-1:
            continue
    
        name = fname.split('_')[0]    
        samples[fname] = fname

        print 'found',filename

sigmas=[]

params={}
legs=["l1","l2"]


plotters=[]
names = []
for name in samples.keys():
    plotters.append(TreePlotter(args[0]+'/'+samples[name]+'.root','AnalysisTree'))
    plotters[-1].setupFromFile(args[0]+'/'+samples[name]+'.pck')
    plotters[-1].addCorrectionFactor('xsec','tree')
    plotters[-1].addCorrectionFactor('genWeight','tree')
    plotters[-1].addCorrectionFactor('puWeight','tree')
    if options.triggerW: plotters[-1].addCorrectionFactor('triggerWeight','tree')	
    corrFactor = options.corrFactorW
    if samples[name].find('Z') != -1: corrFactor = options.corrFactorZ
    if samples[name].find('W') != -1: corrFactor = options.corrFactorW
    plotters[-1].addCorrectionFactor(corrFactor,'flat')
    names.append(samples[name])
    
print 'Fitting Mjet:' 


histos2D_l2={}
histos2D={}
histos2D_nonRes={}
histos2D_nonRes_l2={}

for p in range(0,len(plotters)):

     key ="Wjets"
     if str(names[p]).find("ZJets")!=-1: key = "Zjets"
     if str(names[p]).find("TT")!=-1: key = "TTbar"
     print "make histo for "+names[p]
     
     if not key in histos2D.keys():
      histos2D_nonRes [key] = plotters[p].drawTH2("jj_l1_softDrop_mass:jj_l2_softDrop_mass",options.cut+"*(jj_l1_mergedVTruth==0)*(jj_l1_softDrop_mass>55&&jj_l1_softDrop_mass<215)","1",80,55,215,80,55,215)
      histos2D_nonRes [key].SetName(key+"_nonResl1")
     
      histos2D [key] = plotters[p].drawTH2("jj_l1_softDrop_mass:jj_l2_softDrop_mass",options.cut+"*(jj_l1_mergedVTruth==1)*(jj_l1_softDrop_mass>55&&jj_l1_softDrop_mass<215)","1",80,55,215,80,55,215)
      histos2D [key].SetName(key+"_Resl1")
      
      histos2D_nonRes_l2 [key] = plotters[p].drawTH2("jj_l2_softDrop_mass:jj_l1_softDrop_mass",options.cut+"*(jj_l2_mergedVTruth==0)*(jj_l2_softDrop_mass>55&&jj_l2_softDrop_mass<215)","1",80,55,215,80,55,215)
      histos2D_nonRes_l2 [key].SetName(key+"_nonResl2")
     
      histos2D_l2 [key] = plotters[p].drawTH2("jj_l2_softDrop_mass:jj_l1_softDrop_mass",options.cut+"*(jj_l2_mergedVTruth==1)*(jj_l2_softDrop_mass>55&&jj_l2_softDrop_mass<215)","1",80,55,215,80,55,215)
      histos2D_l2 [key].SetName(key+"_Resl2")
     else:
      histos2D_nonRes [key].Add(plotters[p].drawTH2("jj_l1_softDrop_mass:jj_l2_softDrop_mass",options.cut+"*(jj_l1_mergedVTruth==0)*(jj_l1_softDrop_mass>55&&jj_l1_softDrop_mass<215)","1",80,55,215,80,55,215))
      histos2D [key].Add(plotters[p].drawTH2("jj_l1_softDrop_mass:jj_l2_softDrop_mass",options.cut+"*(jj_l1_mergedVTruth==1)*(jj_l1_softDrop_mass>55&&jj_l1_softDrop_mass<215)","1",80,55,215,80,55,215))
      histos2D_nonRes_l2 [key].Add(plotters[p].drawTH2("jj_l2_softDrop_mass:jj_l1_softDrop_mass",options.cut+"*(jj_l2_mergedVTruth==0)*(jj_l2_softDrop_mass>55&&jj_l2_softDrop_mass<215)","1",80,55,215,80,55,215))
      histos2D_l2 [key].Add(plotters[p].drawTH2("jj_l2_softDrop_mass:jj_l1_softDrop_mass",options.cut+"*(jj_l2_mergedVTruth==1)*(jj_l2_softDrop_mass>55&&jj_l2_softDrop_mass<215)","1",80,55,215,80,55,215))

for key in histos2D.keys():      
     #add together the two legs to make the fit more stable
     histos2D[key].Add(histos2D_l2[key])
     histos2D_nonRes[key].Add(histos2D_nonRes_l2[key])
     
     #scale to lumi for nice visualization
     histos2D[key].Scale(float(lumi)) 
     histos2D_l2[key].Scale(float(lumi))
     histos2D_nonRes[key].Scale(float(lumi))
     histos2D_nonRes_l2[key].Scale(float(lumi))
 
############################
tmpfile = ROOT.TFile("test.root","RECREATE")
for key in histos2D.keys():
    
    #histos2D_l2[key].Write()
    histos2D_nonRes[key].Write()
    #histos2D_nonRes_l2[key].Write()
    histos2D[key].Write()


###########################
 

histos = {}
histos_nonRes = {}
scales={}
scales_nonRes={}

purity = "LPLP"
if options.output.find("HPHP")!=-1:purity = "HPHP"
if options.output.find("HPLP")!=-1:purity = "HPLP"
if options.output.find("LPHP")!=-1:purity = "LPHP"
if options.output.find("VV")!=-1: purity = 'VV_'+purity
else: purity = 'VH_'+purity


fitter=Fitter(['x'])
fitter.jetResonanceVjets('model','x')

if options.fixPars!="1":
    fixedPars =options.fixPars.split(',')
    if len(fixedPars) > 0:
	print "   - Fix parameters: ", fixedPars
	for par in fixedPars:
	    parVal = par.split(':')
	    fitter.w.var(parVal[0]).setVal(float(parVal[1]))
	    fitter.w.var(parVal[0]).setConstant(1) 
 
for key in histos2D.keys():
    histos_nonRes [key] = histos2D_nonRes[key].ProjectionY()
    histos  [key] = histos2D[key].ProjectionY()
    
    histos_nonRes[key].SetName(key+"_nonRes")
    histos [key].SetName(key)
    scales [key] = histos[key].Integral()
    scales_nonRes [key] = histos_nonRes[key].Integral()



# combine ttbar and wjets contributions:  
Wjets = histos["Wjets"]
Wjets_nonRes = histos_nonRes["Wjets"]
if 'TTbar' in histos.keys(): Wjets.Add(histos["TTbar"]); Wjets_nonRes.Add(histos_nonRes["TTbar"])

keys = ["Wjets"]
Wjets_params = doFit(fitter,Wjets,Wjets_nonRes,"Wjets_TTbar_"+purity)


params.update(Wjets_params)
params["ratio_Res_nonRes"]= {'ratio':scales["Wjets"]/scales_nonRes["Wjets"] }

if 'Zjets' in histos.keys():
    keys.append("Zjets")
    fitterZ=Fitter(['x'])
    fitterZ.jetResonanceVjets('model','x')
    Zjets_params = doFit(fitterZ,histos["Zjets"],histos_nonRes["Zjets"],"Zjets_"+purity)
    params.update(Wjets_params)
    params.update(Zjets_params)
    params["ratio_Res_nonRes"]= {'ratio': scales["Wjets"]/scales_nonRes["Wjets"] , 'ratio_Z': scales["Zjets"]/scales_nonRes["Zjets"]}
if "Zjets" in histos.keys() and "TTbar" in histos.keys():
    params["ratio_Res_nonRes"]= {'ratio': scales["Wjets"]/scales_nonRes["Wjets"] , 'ratio_Z':  scales["Zjets"]/scales_nonRes["Zjets"],'ratio_TT':  scales["TTbar"]/scales_nonRes["TTbar"]}
print "going to call fitter.drawVjets for",purity
print "histos "+str(histos)	  
print "histos_nonRes "+str(histos_nonRes)	
print "scales "+str(scales)	  
print "scales_nonRes "+str(scales_nonRes)	
fitter.drawVjets("Vjets_mjetRes_"+purity+".pdf",histos,histos_nonRes,scales,scales_nonRes)
del histos,histos_nonRes,fitter,fitterZ

if options.store!="":
    print "write to file "+options.store
    f=open(options.store,"w")
    for par in params:
        f.write(str(par)+ " = " +str(params[par])+"\n")

 




