// ROOT headers

#ifdef __CLING__
gSystem->AddIncludePath("-I/$WORK/Delphes/");
R__LOAD_LIBRARY(libDelphes.so)
#include "classes/DelphesClasses.h"
#include "external/ExRootAnalysis/ExRootTreeReader.h"
#include "external/fastjet/contribs/LundPlugin/LundWithSecondary.hh"
#include "external/fastjet/contribs/LundPlugin/LundJSON.hh"
#include "external/fastjet/PseudoJet.hh"
#include <cstdlib> // for integer abs
#include <cmath>   // for floating point abs

//#include <stringstream>
#endif


void read_event(vector<fastjet::PseudoJet> &event, TClonesArray *branchParticle, TObject *object, GenParticle *particle, const char * stage) {


    // read gen particles and apply selection criteria to build the event for jet clustering
    for (int i = 0; i < branchParticle->GetEntriesFast(); i++) {
        GenParticle *particle = (GenParticle*) branchParticle->At(i);

        // Check if the particle is accessible        
        if (particle != nullptr) {
            double particle_PID = particle->PID;
        } 
        else {               
             // Handle the case where particle is a null pointer.
             std::cout << "particle is a null pointer." << std::endl;
        }

        double particle_PID = particle->PID;                        
        double particle_Status = particle->Status;

        if (std::strcmp(stage, "darkHadron") == 0) {

            if (((std::abs(particle_Status) == 1) && ((std::abs(particle_PID) > 4900000) ))){
                fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
                event.push_back(pseudoJet);
            }

        }
        else if (std::strcmp(stage, "smHadron") == 0) {

            if ((std::abs(particle_Status) == 1) &&
               ((std::abs(particle_PID) > 100) && (std::abs(particle_PID) < 1000000000))){

                fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
                event.push_back(pseudoJet);
            }

        }
        else if (std::strcmp(stage, "visible") == 0) {

            //Invisible particles ids 12, 14, 16, 51, 53
             if ((std::abs(particle_Status) == 1) &&
               ((std::abs(particle_PID) != 12) && (std::abs(particle_PID) != 14) && (std::abs(particle_PID) != 16) && (std::abs(particle_PID) != 51) && (std::abs(particle_PID) != 53))){

                fastjet::PseudoJet pseudoJet(particle->P4().Px(), particle->P4().Py(), particle->P4().Pz(), particle->P4().E());
                event.push_back(pseudoJet);
            }

        }
        else {
            std::cout << "Invalid stage specified. Please choose 'darkHadron', 'smHadron', or 'visible'." << std::endl;
             std::cout << "'darkHadron' stage: build LJP using dark hadrons." << std::endl;
             std::cout << "'smHadron' stage: build LJP using SM hadrons." << std::endl;
             std::cout << "'visible' stage: build LJP using all visible particles." << std::endl;
             exit(1);
        }

    }
}


//add as input also R, ptmin, ptmax, set to some default value, but can be changed when calling the function in the macro
void process_to_json(const char* fileName, const char* Output_path, const char * stage = "", double R = 1.0, double ptmin = 200.0, double ptmax = 8000.0) {
   

    gSystem->Load("libDelphes");
    TChain chain("Delphes");
    chain.Add(fileName);
    ExRootTreeReader *treeReader = new ExRootTreeReader(&chain);
    Long64_t numberOfEntries = treeReader->GetEntries();
    TClonesArray *branchParticle = treeReader->UseBranch("Particle");
    
    TObject *object;
    GenParticle *particle;


    stringstream ss;
    ss << Output_path; 
    string filename = ss.str();

    cout << "# writing declusterings of primary and secondary plane to file "
    << filename << endl;
    
    
    ofstream outfile;
    outfile.open(filename);
    // Loop over all events and apply first anti-kt clustering algorithm
    for(Int_t entry = 0; entry < (numberOfEntries < 40000L ? numberOfEntries : 40000L); ++entry) {
        treeReader->ReadEntry(entry);
        
        vector<fastjet::PseudoJet> event;
        read_event(event, branchParticle , object,particle, stage);
        
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
        //----------------------------------------------------------
        // create an instance of LundWithSecondary, with default options
        fastjet::contrib::SecondaryLund_mMDT secondary;
        fastjet::contrib::LundWithSecondary lund(&secondary);
        
        cout << lund.description() << endl;

        // Loop over all clustered jets and apply C/A algorithm to declustering
        for (unsigned ijet = 0; ijet < jets.size(); ijet++) {
            cout << endl << "Lund coordinates ( ln 1/Delta, ln kt ) of declusterings of jet "
            << ijet << " are:" << endl;
            vector<fastjet::contrib::LundDeclustering> declusts = lund.primary(jets[ijet]);
            
            // Loop in a jet over its declustered component and extract Lund coordinates

            for (int idecl = 0; idecl < declusts.size(); idecl++) {
                pair<double,double> coords = declusts[idecl].lund_coordinates();
                cout << "(" << coords.first << ", " << coords.second << ")";
                if (idecl < declusts.size() - 1) cout << "; ";
            }
            
            cout << endl;
            
            // outputs the primary Lund plane
            lund_to_json(outfile, declusts); outfile << endl;
        }
        
        cout << endl << "# Wrote declustering in file " << filename  << endl;
        
    }
    
    outfile.close();
}
