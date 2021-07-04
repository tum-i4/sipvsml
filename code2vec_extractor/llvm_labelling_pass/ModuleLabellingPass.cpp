// USAGE:
//    1. Legacy PM
//      opt -load libHelloWorld.dylib -legacy-hello-world -disable-output `\`
//        <input-llvm-file>
//    2. New PM
//      opt -load-pass-plugin=libHelloWorld.dylib -passes="hello-world" `\`
//        -disable-output <input-llvm-file>
//
//
// License: MIT
//=============================================================================
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"

using namespace llvm;

static cl::opt<std::string> BCFilePath("bc-file-path", cl::desc("Specify input bc file path "), cl::value_desc("LABELED-BCs/simple-cov/BCF30/"));

// No need to expose the internals of the pass to the outside world - keep
// everything in an anonymous namespace.
namespace {
    std::string getInstLabel(const llvm::Instruction &inst) {
        if (inst.getMetadata("oh_hash")) {
            return "oh_hash";
        } else if (inst.getMetadata("oh_verify")) {
            return "oh_verify";
        } else if (inst.getMetadata("cfi_register")) {
            return "cfi_register";
        } else if (inst.getMetadata("cfi_verify")) {
            return "cfi_verify";
        } else if (inst.getMetadata("sc_guard")) {
            return "sc_guard";
        } else {
            return "none";
        }
    }

    std::string getFileName(std::string path) {
        const size_t pos = path.find_last_of('/');
        if (pos != std::string::npos) {
            return path.substr(pos + 1, path.size());
        }
        return path;
    }

    std::string getUniqueBlockName(const BasicBlock &BB, const Function &F) {
        // need this to keep legacy block identifier
        std::string Str = BCFilePath + getFileName(F.getParent()->getModuleIdentifier());
        Str += F.getName();
        std::string BBStr;
        llvm::raw_string_ostream OS(BBStr);
        BB.printAsOperand(OS, false);
        BBStr = OS.str();
        return Str + BBStr;
    }

    std::size_t getUniqueBlockUID(const BasicBlock &BB, const Function &F) {
        std::hash<std::string> hasher;
        auto hashed = hasher(getUniqueBlockName(BB, F));
        return hashed;
    }

    std::string getBlockLabel(const BasicBlock &BB) {
        std::string label = "none";
        for (const Instruction &I: BB) {
            std::string instrLabel = getInstLabel(I);
            if (instrLabel != "none") {
                label = instrLabel;
            }
        }
        return label;
    }

    // This method implements what the pass does
    void visitor(Module &M) {
        for (Function &F: M) {
            for (BasicBlock& bb : F){
                errs() << getUniqueBlockName(bb, F) << "\t" << getUniqueBlockUID(bb, F) << "\t" << getBlockLabel(bb) << "\n";
            }
        }
    }

// New PM implementation
    struct ModuleLabelling : PassInfoMixin<ModuleLabelling> {
        // Main entry point, takes IR unit to run the pass on (&F) and the
        // corresponding pass manager (to be queried if need be)
//        PreservedAnalyses run(Function &F, FunctionAnalysisManager &) {
//            visitor(F);
//            return PreservedAnalyses::all();
//        }

        PreservedAnalyses run(Module &M, ModuleAnalysisManager &) {
            visitor(M);
            return PreservedAnalyses::all();
        }
    };

// Legacy PM implementation
    struct LegacyModuleLabelling : public ModulePass {
        static char ID;
        LegacyModuleLabelling() : ModulePass(ID) {}
        // Main entry point - the name conveys what unit of IR this is to be run on.
        bool runOnModule(Module &M) override {
            visitor(M);
            // Doesn't modify the input unit of IR, hence 'false'
            return false;
        }
    };
} // namespace

//-----------------------------------------------------------------------------
// New PM Registration
//-----------------------------------------------------------------------------
llvm::PassPluginLibraryInfo getModuleLabellingPluginInfo() {
    return {LLVM_PLUGIN_API_VERSION, "ModuleLabelling", LLVM_VERSION_STRING,
            [](PassBuilder &PB) {
                PB.registerPipelineParsingCallback(
                        [](StringRef Name, ModulePassManager &MPM,
                           ArrayRef<PassBuilder::PipelineElement>) {
                            if (Name == "module-labelling") {
                                MPM.addPass(ModuleLabelling());
                                return true;
                            }
                            return false;
                        });
            }};
}

// This is the core interface for pass plugins. It guarantees that 'opt' will
// be able to recognize ModuleLabelling when added to the pass pipeline on the
// command line, i.e. via '-passes=module-labelling'
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return getModuleLabellingPluginInfo();
}

//-----------------------------------------------------------------------------
// Legacy PM Registration
//-----------------------------------------------------------------------------
// The address of this variable is used to uniquely identify the pass. The
// actual value doesn't matter.
char LegacyModuleLabelling::ID = 1;

// This is the core interface for pass plugins. It guarantees that 'opt' will
// recognize LegacyHelloWorld when added to the pass pipeline on the command
// line, i.e.  via '--legacy-module-labelling'
static RegisterPass<LegacyModuleLabelling>
        X("legacy-module-labelling", "Basic Block Labelling Pass",
          true, // This pass doesn't modify the CFG => true
          false // This pass is not a pure analysis pass => false
);
