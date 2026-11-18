import Foundation
import RealityKit
let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1], isDirectory: true)
let output = URL(fileURLWithPath: args[2], isDirectory: true)
let detail: PhotogrammetrySession.Request.Detail = args[3] == "full" ? .full : (args[3] == "raw" ? .raw : .medium)
var cfg = PhotogrammetrySession.Configuration()
cfg.sampleOrdering = .sequential
cfg.featureSensitivity = .high
let session = try PhotogrammetrySession(input: input, configuration: cfg)
let sem = DispatchSemaphore(value: 0)
Task {
  for try await out in session.outputs {
    switch out {
    case .requestProgress(_, let f): print(String(format: "progress %.0f%%", f*100)); fflush(stdout)
    case .requestComplete(_, let r): print("complete", r)
    case .requestError(_, let e): print("ERROR", e)
    case .processingComplete: print("DONE"); sem.signal()
    case .invalidSample(let id, let reason): print("invalid", id, reason)
    case .skippedSample(let id): print("skipped", id)
    default: break
    }
    fflush(stdout)
  }
}
try session.process(requests: [.modelFile(url: output, detail: detail)])
sem.wait()
