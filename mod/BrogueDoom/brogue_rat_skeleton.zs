// Original Project Broom source, AGPL-3.0-or-later. UZDoom 5.0 bone offsets.
// Brogue/native reconciliation owns clips, positions, visibility and lifetime.
class BrogueRatSkeletalProxy : BrogueMonsterProxyBase
{
    int PresentationClip; // RatClip copied by PlayRatClip; never gameplay state.
    double TailBend, PreviousTailBend, LastVisualYaw, VisualPhase;
    bool PoseInitialized;
    ui PrecalculatedAnimationFrame DetailPose;
    ui Array<bool> DetailMask;

    override void Tick()
    {
        Super.Tick();
        if (!PoseInitialized)
        {
            LastVisualYaw = angle;
            VisualPhase = pos.x * 0.13 + pos.y * 0.17;
            PoseInitialized = true;
        }
        PreviousTailBend = TailBend;
        // React only to the already-projected facing. No target search or AI.
        double turn = clamp(deltaangle(LastVisualYaw, angle), -90.0, 90.0);
        LastVisualYaw = angle;
        bool suppressed = PresentationClip > 1 || bINVISIBLE || alpha < 0.99;
        if (suppressed)
        {
            TailBend = PreviousTailBend = 0;
            // Never call ClearBoneOffsets on an unrendered actor: UZDoom 5.0
            // indexes override slot zero even when it has not been allocated.
            // Hidden poses aren't rendered; AnimateBones replaces every offset
            // on the first visible frame, including identity for combat/death.
        }
        else
            TailBend = clamp(TailBend * 0.78 - turn * 0.12, -10.0, 10.0);
    }

    override void AnimateBones(double ticfrac)
    {
        // One cached local-TRS batch, no per-bone CalcBones or world-bone queries.
        if (!DetailPose)
        {
            DetailPose = new("PrecalculatedAnimationFrame");
            DetailPose.frameData.Resize(28);
            DetailMask.Resize(28);
            for (int i = 0; i < 28; i++)
            {
                DetailPose.frameData[i].translation = (0,0,0);
                DetailPose.frameData[i].scaling = (1,1,1);
                DetailMask[i] = i == 4 || i == 6 || i == 7 || i >= 20;
            }
        }
        for (int i = 0; i < 28; i++)
            DetailPose.frameData[i].rotation = Quat(0,0,0,1);
        let quality = CVar.FindCVar('brg_fx_quality');
        if (PresentationClip <= 1 && !bINVISIBLE && alpha >= 0.99 && quality && quality.GetInt() > 0)
        {
            double phase = (level.totaltime + ticfrac) * 360.0 / 109.0 + VisualPhase;
            double detail = quality.GetInt() > 1 ? 1.25 : 1.0;
            // Keep neck, jaw, root and all leg joints entirely in the authored clip.
            DetailPose.frameData[4].rotation = Quat.FromAngles(sin(phase)*2*detail, sin(phase*2)*1.5*detail, 0);
            DetailPose.frameData[6].rotation = Quat.FromAngles(0,0,(max(0,sin(phase*1.7)) ** 12)*9*detail);
            DetailPose.frameData[7].rotation = Quat.FromAngles(0,0,-(max(0,sin(phase*1.7+117)) ** 12)*9*detail);
            double bend = PreviousTailBend + (TailBend-PreviousTailBend)*ticfrac;
            for (int i = 20; i < 28; i++)
                DetailPose.frameData[i].rotation = Quat.FromAngles(
                    bend*(i-19)/36.0 + sin(phase-(i-20)*26)*0.65*detail, 0, 0);
        }
        // Identity values also clear old offsets for death, hidden state and Basic.
        // SB_ADD combines each local offset with the current skeletal clip.
        OverwriteBonesMask(DetailPose, DetailMask, SB_ADD);
    }
}
