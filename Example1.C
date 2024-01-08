// ROOT headers

#ifdef __CLING__
R__LOAD_LIBRARY(libDelphes)
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/fastjet/contribs/LundPlugin/LundWithSecondary.hh"
#include "external/fastjet/contribs/LundPlugin/LundJSON.hh"
#include "external/fastjet/PseudoJet.hh"
#include <cstdlib> // for integer abs
#include <cmath>   // for floating point abs

//#include <stringstream>
#endif

//using namespace std;
//using namespace fastjet;

/*
void read_event(vector<fastjet::PseudoJet> &event, TClonesArray *branchJet, Jet * jet, TObject *object, GenParticle *particle) {
    
    // read jets from branch and convert them to fastjet::PseudoJet
    for (int i = 0; i < branchJet->GetEntriesFast(); i++) {
        Jet *jet = (Jet*) branchJet->At(i);
        //Loop over all jets constituents
        for(int j = 0; j < jet->Constituents.GetEntriesFast(); ++j)
        {
            object = jet->Constituents.At(j);
            // Check if the constituent is accessible
            if(object == 0) continue;
            if(object->IsA() == GenParticle::Class())
            {
                
                particle = (GenParticle*) object;
                double particle_PID = particle->PID;
                double particle_Status = particle->Status;
                double mother_List = particle -> M1;
                double daughter_List = particle -> D1;
                double mother_PID;
                std::cout << "particle_PID: " << particle_PID << std::endl;
                std::cout << "particle_Status: " << particle_Status << std::endl;
                break;
                if((std::abs(particle_PID)>490000) && (std::abs(particle_Status) == 91))
                {
                
                    fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
                    event.push_back(pseudoJet);
                }    
                

            }
        }
    }
}
*/
void read_event(vector<fastjet::PseudoJet> &event, TClonesArray *branchParticle, TObject *object, GenParticle *particle) {




    // read jets from branch and convert them to fastjet::PseudoJet
    for (int i = 0; i < branchParticle->GetEntriesFast(); i++) {
        GenParticle *particle = (GenParticle*) branchParticle->At(i);
        // Loop over all jets constituents
       
            
            // Check if the constituent is accessible

                
        if (particle != nullptr) {
            double particle_PID = particle->PID;
        } 
        else {                // Handle the case where particle is a null pointer.
             std::cout << "particle is a null pointer." << std::endl;
        }

        double particle_PID = particle->PID;
                        
        double particle_Status = particle->Status;
        if(((std::abs(particle_Status) == 1)) && (std::abs(particle_PID) != 12) && (std::abs(particle_PID) != 14) && (std::abs(particle_PID) != 16)) {
            fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
            event.push_back(pseudoJet);
            //&& (std::abs(particle_PID) != 12) && (std::abs(particle_PID) != 14) && (std::abs(particle_PID) != 16)
        
            //| (std::abs(particle_Status) == 83) | (std::abs(particle_Status) == 84)) && ((std::abs(particle_PID) > 4900000))
            //  if(((std::abs(particle_Status) == 1)))     {
            //fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
            //event.push_back(pseudoJet);
        }    //}
    }
}
//(std::abs(particle_PID)>490000) && 

//const char* fileName, const char* Output_path
void Example1(const char* fileName, const char* Output_path){
    // ROOT and Delphes setup
    
        // Function to list all trees in the file
    //auto list_trees = [fileName](){
       // TFile *f = TFile::Open(fileName);
        //TIter nextkey(f->GetListOfKeys());
        //TKey *key;
        //while ((key = (TKey*)nextkey())) {
            //TClass *cl = gROOT->GetClass(key->GetClassName());
            //if (!cl->InheritsFrom("TTree")) continue;
            //TTree *tree = (TTree*)key->ReadObj();
            //cout << "Found tree: " << tree->GetName() << "\n";
        //}
        //f->Close();
    //};

    //list_trees();

    gSystem->Load("libDelphes");
    TChain chain("Delphes");
    //const char* inputFile = "test_different_Seed_50_Lambda_v_dark_shower.root";  // Just an example, replace with actual path
    chain.Add(fileName);
    //chain.Add(inputFile);
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    Long64_t numberOfEntries = treeReader->GetEntries();
    TClonesArray *branchJet = treeReader->UseBranch("GenJet");
    TClonesArray *branchParticle = treeReader->UseBranch("Particle");
    
    Jet *jet;
    TObject *object;
    GenParticle *particle;

   
    
    // first get some anti-kt jets
    double R = 1, ptmin = 400.0, ptmax = 8000.0;
    string slurm_job_id = getenv("SLURM_JOB_ID");
    stringstream ss;
    ss << Output_path << slurm_job_id << "/jets_Scan.json";
    string filename = ss.str();

    cout << "# writing declusterings of primary and secondary plane to file "
    << filename << endl;
    

    
    //string filename = "jetsDShower.json";
    //cout << "# writing declusterings of primary and secondary plane to file "
    //<< filename << endl;
    
    ofstream outfile;
    outfile.open(filename);
    // Loop over all events
    for(Int_t entry = 0; entry < 40000; ++entry) {
        treeReader->ReadEntry(entry);
        
        vector<fastjet::PseudoJet> event;
        read_event(event, branchParticle , object,particle);
    
        cout << "# Reading event : " << entry << " / with " << event.size() << " particles" << endl;
        
        fastjet::JetDefinition jet_def(fastjet::antikt_algorithm, R);
        fastjet::ClusterSequence cs(event, jet_def);
        vector<fastjet::PseudoJet> jets = sorted_by_pt(cs.inclusive_jets(ptmin));
        for(auto it = jets.begin(); it != jets.end();){
            if(it->perp() > ptmax){
                it = jets.erase(it);
            }else{
                ++it;
            }
        }
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
