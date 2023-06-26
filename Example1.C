// ROOT headers

#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes)
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/fastjet/contribs/LundPlugin/LundWithSecondary.hh"
#include "external/fastjet/contribs/LundPlugin/LundJSON.hh"
#include "external/fastjet/PseudoJet.hh"
#endif

//using namespace std;
//using namespace fastjet;


void read_event(vector<fastjet::PseudoJet> &event, TClonesArray *branchJet, Jet * jet, TObject *object, GenParticle *particle) {
    
    // read jets from branch and convert them to fastjet::PseudoJet
    for (int i = 0; i < branchJet->GetEntriesFast(); i++) {
        Jet *jet = (Jet*) branchJet->At(i);
        // Loop over all jet's constituents
        for(int j = 0; j < jet->Constituents.GetEntriesFast(); ++j)
        {
            object = jet->Constituents.At(j);
            // Check if the constituent is accessible
            if(object == 0) continue;
            if(object->IsA() == GenParticle::Class())
            {
                particle = (GenParticle*) object;
                fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
                event.push_back(pseudoJet);
            }
        }
    }
}

void Example1(){
    // ROOT and Delphes setup
    gSystem->Load("libDelphes");
    TChain chain("Delphes");
    const char* inputFile = "/Users/cesarecazzaniga/test_delphes/Delphes/delphes_nolhe.root";  // Just an example, replace with actual path
    chain.Add(inputFile);
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    Long64_t numberOfEntries = treeReader->GetEntries();
    TClonesArray *branchJet = treeReader->UseBranch("GenJet");
    TClonesArray *branchParticle = treeReader->UseBranch("Particle");
    
    Jet *jet;
    TObject *object;
    GenParticle *particle;
    
    // first get some anti-kt jets
    double R = 1.0, ptmin = 50.0;
    
    string filename = "jets.json";
    cout << "# writing declusterings of primary and secondary plane to file "
    << filename << endl;
    
    ofstream outfile;
    outfile.open(filename);
    
    // Loop over all events
    for(Int_t entry = 0; entry < 3; ++entry) {
        treeReader->ReadEntry(entry);
        
        vector<fastjet::PseudoJet> event;
        read_event(event, branchJet,jet , object,particle);
    
        cout << "# Reading event : " << entry << " / with " << event.size() << " particles" << endl;
        
        fastjet::JetDefinition jet_def(fastjet::antikt_algorithm, R);
        fastjet::ClusterSequence cs(event, jet_def);
        vector<fastjet::PseudoJet> jets = sorted_by_pt(cs.inclusive_jets(ptmin));
        
        cout  << "Number of clustered jets: " << jets.size() << endl;
        //----------------------------------------------------------
        // create an instance of LundWithSecondary, with default options
        fastjet::contrib::SecondaryLund_mMDT secondary;
        fastjet::contrib::LundWithSecondary lund(&secondary);
        
        cout << lund.description() << endl;
        
        for (unsigned ijet = 0; ijet < jets.size(); ijet++) {
            cout << endl << "Lund coordinates ( ln 1/Delta, ln kt ) of declusterings of jet "
            << ijet << " are:" << endl;
            vector<fastjet::contrib::LundDeclustering> declusts = lund.primary(jets[ijet]);
            
            for (int idecl = 0; idecl < declusts.size(); idecl++) {
                pair<double,double> coords = declusts[idecl].lund_coordinates();
                cout << "(" << coords.first << ", " << coords.second << ")";
                if (idecl < declusts.size() - 1) cout << "; ";
            }
            
            cout << endl;
            
            // outputs the primary Lund plane
            lund_to_json(outfile, declusts); outfile << endl;
            // outputs the full Lund tree
            //to_json(cout, lund_gen, jets[ijet]); cout << endl;
        }
        
        cout << endl << "# Wrote declustering in file " << filename  << endl;
        
    }
    
    outfile.close();
}
