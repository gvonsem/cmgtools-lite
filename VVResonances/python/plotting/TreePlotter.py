import ROOT
import sys,commands
from array import array
import pickle
from PlotterBase import PlotterBase
from array import array
import random

class TreePlotter(PlotterBase):

    def __init__(self,file,tree,weight = "1"):
        self.file = ROOT.TFile(file)
        print self.file 
        print tree
        self.tree = self.file.Get(tree)
        if tree ==0:
            print "Tree not found\n"
            sys.exit()
        self.weight=weight
        super(TreePlotter,self).__init__()
        self.random=ROOT.TRandom(101082)
        self.N=self.tree.GetEntries()

    def setupFromFile(self,filename):
        f=open(filename)
        data=pickle.load(f)
        weightinv = float(data['events'])
        self.addCorrectionFactor(1./weightinv,'flat')
        self.weightinv=weightinv
            
    def applySmoothing(self):
        self.smooth=True

    def drawTH1(self,var,cuts,lumi,bins,min,max,titlex = "",units = "",drawStyle = "HIST"):
        h = ROOT.TH1D("tmpTH1","",bins,min,max)
        h.Sumw2()
        h.SetLineStyle(self.linestyle)
        h.SetLineColor(self.linecolor)
        h.SetLineWidth(self.linewidth)
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.SetMarkerStyle(self.markerstyle)
        if units=="":
            h.GetXaxis().SetTitle(titlex)
        else:
            h.GetXaxis().SetTitle(titlex+ " ["+units+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*("+str(corr['value'])+")" 
        self.tree.Draw(var+">>tmpTH1","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")

        return h


    def randomEvent(self):
        i=int(self.random.Rndm()*self.N)
        self.tree.GetEntry(i)       


    def drawTH2(self,var,cuts,lumi,binsx,minx,maxx,binsy,miny,maxy,titlex = "",unitsx = "",titley="",unitsy="", drawStyle = "COLZ"):
        h = ROOT.TH2D("tmpTH2","",binsx,minx,maxx,binsy,miny,maxy)
        h.Sumw2()
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*"+str(corr['value']) 
        self.tree.Draw(var+">>tmpTH2","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")

        return h



    def drawProfile(self,var,cuts,lumi,binsx,minx,maxx,miny,maxy,titlex = "",unitsx = "",titley="",unitsy="", drawStyle = "COLZ"):
        h = ROOT.TProfile("tmpTH2","",binsx,minx,maxx,miny,maxy)
        h.Sumw2()
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*"+str(corr['value']) 
        self.tree.Draw(var+">>tmpTH2","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")

        return h




    def drawTH3(self,var,cuts,lumi,binsx,minx,maxx,binsy,miny,maxy,binsz,minz,maxz,titlex = "",unitsx = "",titley="",unitsy="", drawStyle = "COLZ"):
        h = ROOT.TH3D("tmpTH3","",binsx,minx,maxx,binsy,miny,maxy,binsz,minz,maxz)
        h.Sumw2()
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*"+str(corr['value']) 
        self.tree.Draw(var+">>tmpTH3","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")
        return h



    def drawTH2Binned(self,var,cuts,lumi,binningx,binningy,titlex = "",unitsx = "",titley="",unitsy="", drawStyle = "COLZ"):
        h = ROOT.TH2D("tmpTH2","",len(binningx)-1,array('f',binningx),len(binningy)-1,array('f',binningy))
        h.Sumw2()
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*"+str(corr['value']) 
        self.tree.Draw(var+">>tmpTH2","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")

        return h


    def drawTH3Binned(self,var,cuts,lumi,binningx,binningy,binningz,titlex = "",unitsx = "",titley="",unitsy="",titlez="",unitsz="", drawStyle = "COLZ"):
        h = ROOT.TH3D("tmpTH3","",len(binningx)-1,array('f',binningx),len(binningy)-1,array('f',binningy),len(binningz)-1,array('f',binningz))
        h.Sumw2()
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")
        h.GetYaxis().SetTitle(titley+ " ["+unitsy+"]")
        h.GetZaxis().SetTitle(titlez+ " ["+unitsz+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*"+str(corr['value']) 
        self.tree.Draw(var+">>tmpTH3","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")

        return h
    

    
    def drawTH1Binned(self,var,cuts,lumi,binningx,titlex = "",unitsx = "", drawStyle = "COLZ"):
        h = ROOT.TH1D("tmpTH1","",len(binningx)-1,array('f',binningx))
        h.Sumw2()
        h.SetFillStyle(self.fillstyle)
        h.SetFillColor(self.fillcolor)
        h.GetXaxis().SetTitle(titlex+ " ["+unitsx+"]")

        #Apply correction factors
        corrString='1'
        for corr in self.corrFactors:
                corrString = corrString+"*"+str(corr['value']) 
        self.tree.Draw(var+">>tmpTH1","("+cuts+")*"+lumi+"*"+self.weight+"*("+corrString+")","goff")

        return h



    def drawEff1D(self,hD,hN,var,denom,num,titlex = "", units = ""):
        self.tree.Draw(var+">>denom","("+denom+")*"+self.weight,"goff")
        self.tree.Draw(var+">>num","("+denom+"&&"+num+")*"+self.weight,"goff")
        graph = ROOT.TGraphAsymmErrors();
        graph.Divide(hN,hD);
        graph.SetName('efficiency')
        graph.SetLineStyle(self.linestyle)
        graph.SetLineColor(self.linecolor)
        graph.SetLineWidth(self.linewidth)
        graph.SetFillStyle(self.fillstyle)
        graph.SetFillColor(self.fillcolor)
        graph.SetMarkerStyle(self.markerstyle)
        if len(units) >0 :
            graph.GetXaxis().SetTitle(titlex+ " ["+units+"]")
        else:
            graph.GetXaxis().SetTitle(titlex)
    
        graph.Draw("AP");
        return graph


    def drawEff2D(self,hD,hN,var,denom,num,titlex = "", unitsx = "",titley = "", unitsy = ""):
        self.tree.Draw(var+">>denom","("+denom+")*"+self.weight,"goff")
        self.tree.Draw(var+">>num","("+denom+"&&"+num+")*"+self.weight,"goff")
        hErrU = hD.Clone()
        hErrU.SetName("hErr")
        hErrD = hD.Clone()
        hErrD.SetName("hErr")

        hEff = hD.Clone()
        hEff.SetName("hEff")

        for i in range(1,hD.GetNbinsX() + 1):
            for j in range(1,hD.GetNbinsY() + 1):
                n=hN.GetBinContent(i,j)
                d=hD.GetBinContent(i,j)
                if n>0. and d>0.:
                    eff=n/d
                    errUp = ROOT.TEfficiency.ClopperPearson(int(d),int(n),0.68,True)
                    errDwn=ROOT.TEfficiency.ClopperPearson(int(d),int(n),0.68,False)

                    hEff.SetBinContent(i,j,eff)
                    hErrU.SetBinContent(i,j,errUp)
                    hErrD.SetBinContent(i,j,errDwn)
        hEff.Draw("COLZ");        
        hEff.GetXaxis().SetTitle(titlex+" ["+unitsx+"]")
        hErrU.GetXaxis().SetTitle(titlex+" ["+unitsx+"]")
        hErrD.GetXaxis().SetTitle(titlex+" ["+unitsx+"]")
        hEff.GetYaxis().SetTitle(titley+" ["+unitsy+"]")
        hErrU.GetYaxis().SetTitle(titley+" ["+unitsy+"]")
        hErrD.GetYaxis().SetTitle(titley+" ["+unitsy+"]")

        out=dict()
        out['eff']=hEff
        out['effUp']=hErrU
        out['effDwn']=hErrD
        return out
        



    def drawEfficiency(self,var,denom,num,bins,mini,maxi,titlex = "", units = ""):
        hD = ROOT.TH1D("denom","",bins,mini,maxi)
        hN = ROOT.TH1D("num","",bins,mini,maxi)
        hD.Sumw2()
        hN.Sumw2()
        return self.drawEff1D(hD,hN,var,denom,num,titlex,units)


    def makeDataSet(self,var,cut,firstEv=0,lastEv=-1):
        variables=var.split(',')
  
        self.cache=ROOT.TFile("/tmp/%s/cache%i.root"%(commands.getoutput("whoami"),random.randint(0, 1e+6)),"RECREATE")
        # self.cache=ROOT.TFile("cache%i.root"%(random.randint(0, 1e+6)),"RECREATE")
        w=ROOT.RooWorkspace("w","w")
        argset=ROOT.RooArgSet()
        argset2=ROOT.RooArgSet()
        for v in variables:
            w.factory(v+"[-1e+25,1e+25]")
            argset.add(w.var(v))
            argset2.add(w.var(v))
        w.factory("weight[-1e+25,1e+25]")       
        argset.add(w.var('weight'))
        
        data=ROOT.RooDataSet("data","data",argset,"weight")
        if lastEv == -1: lastEv = self.tree.GetEntries()
        print lastEv,firstEv
        reduced = self.tree.CopyTree(cut,"",lastEv,firstEv)
        print "done reduced"
        N=0
        for event in reduced:
            weight = 1.0
            for c in self.corrFactors:
                if c['model']=='flat':
                    weight=weight*c['value']
                if c['model']=='tree':
                    weight=weight*getattr(event,c['value'])
                if c['model']=='branch':
                    weight=weight*getattr(event,c['value'])[0]

            for v in variables:
                argset2.find(v).setVal(getattr(event,v))
                #argset2.find(v).setVal(getattr(event,v)[0])
            data.add(argset2,weight)
            #N=N+1
            #if maxN >0 and N>maxN:
            #    return data
        del self.cache
        return data    




    def drawEfficiency2D(self,var,denom,num,bins1,mini1,maxi1,bins2,mini2,maxi2,titlex = "", unitsx = "",titley = "", unitsy = ""):
        hD = ROOT.TH2D("denom","",bins1,mini1,maxi1,bins2,mini2,maxi2)
        hN = ROOT.TH2D("num","",bins1,mini1,maxi1,bins2,mini2,maxi2)
        hD.Sumw2()
        hN.Sumw2()
        return self.drawEff2D(hD,hN,var,denom,num,titlex,unitsx,titley,unitsy)


    def drawEfficiencyB(self,var,denom,num,binning,titlex = "", units = ""):
        hD = ROOT.TH1D("denom","",len(binning)-1,array('d',binning))
        hN = ROOT.TH1D("num","",len(binning)-1,array('d',binning))
        hD.Sumw2()
        hN.Sumw2()
        return self.drawEff1D(hD,hN,var,denom,num,titlex,units)

    def drawEfficiency2DB(self,var,denom,num,binning1,binning2,titlex = "", unitsx = "",titley = "", unitsy=""):
        hD = ROOT.TH2D("denom","",len(binning1)-1,array('d',binning1),len(binning2)-1,array('d',binning2))
        hN = ROOT.TH2D("num","",len(binning1)-1,array('d',binning1),len(binning2)-1,array('d',binning2))

        hD.Sumw2()
        hN.Sumw2()
        return self.drawEff2D(hD,hN,var,denom,num,titlex,unitsx,titley,unitsy)
